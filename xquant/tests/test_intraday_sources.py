import lzma
from datetime import UTC, datetime

import numpy as np
import pandas as pd
import pytest

from xquant.backtest.engine import MarketArrays, run_backtest
from xquant.config import CostModel
from xquant.data.crosscheck import cross_check_daily
from xquant.data.sources.dukascopy_candles import RECORD, DukascopyCandleSource, check_candles, decode_candles
from xquant.data.sources.mt5 import Mt5CsvSource, server_to_utc
from xquant.errors import DataNotFound, DataQualityError


def _blob(rows, order=("open", "close", "low", "high")):
    """Encode candles with the documented Dukascopy layout (or a deliberately wrong field order)."""
    rec = np.zeros(len(rows), dtype=RECORD)
    for i, r in enumerate(rows):
        rec[i]["t"] = r["t"]
        vals = [r[k] for k in order]
        rec[i]["open"], rec[i]["close"], rec[i]["low"], rec[i]["high"] = vals
        rec[i]["vol"] = r["vol"]
    return lzma.compress(rec.tobytes(), format=lzma.FORMAT_ALONE)


def _hourly_rows(n, base=110000, spread=0, seed=0):
    rng = np.random.default_rng(seed)
    rows, px = [], base
    for h in range(n):
        o = px
        c = o + int(rng.integers(-30, 31))
        hi, lo = max(o, c) + int(rng.integers(0, 10)), min(o, c) - int(rng.integers(0, 10))
        rows.append({"t": h * 3600, "open": o + spread, "close": c + spread, "low": lo + spread, "high": hi + spread,
                     "vol": 0.0 if h % 50 == 49 else 12.5})
        px = c
    return rows


def test_decode_and_format_check():
    rows = _hourly_rows(100)
    df = decode_candles(_blob(rows), datetime(2023, 1, 1, tzinfo=UTC), 1e-5)
    assert df.index[1] == pd.Timestamp("2023-01-01 01:00", tz="UTC")
    assert df["open"].iloc[0] == pytest.approx(1.10)
    check_candles(df, "BID", (0.8, 1.8))
    wrong = decode_candles(_blob(rows, order=("open", "high", "low", "close")), datetime(2023, 1, 1, tzinfo=UTC), 1e-5)
    with pytest.raises(DataQualityError):
        check_candles(wrong, "BID", None)  # misread field order fails loudly
    with pytest.raises(DataQualityError):
        check_candles(df * 10, "BID", (0.8, 1.8))  # wrong point scaling fails loudly


def test_dukascopy_candle_source_end_to_end(tmp_path):
    files = {}
    for month in (0, 1):
        hours = 24 * (31 if month == 0 else 28)
        files[f"2023/{month:02d}/BID_candles_hour_1.bi5"] = _blob(_hourly_rows(hours, seed=month))
        files[f"2023/{month:02d}/ASK_candles_hour_1.bi5"] = _blob(_hourly_rows(hours, spread=8, seed=month))

    def fetch(url):
        key = url.split("/EURUSD/")[1]
        if key not in files:
            raise DataNotFound(url)
        return files[key]

    src = DukascopyCandleSource("EURUSD", "2023-01-01", "2023-04-01", granularity="hour", point=1e-5, min_interval=0,
                                expected_range=[0.8, 1.8], fetch=fetch, cache_dir=tmp_path, workers=2)
    assert src.url_for(datetime(2023, 1, 1), "BID").endswith("/EURUSD/2023/00/BID_candles_hour_1.bi5")
    bars = src.fetch_series()
    assert bars.index[0] == pd.Timestamp("2023-01-01 01:00", tz="UTC")  # stamped at bar close
    assert bars["spread"].median() == pytest.approx(8e-5)
    assert src.provenance["flat_zero_volume_dropped"] > 0
    assert "2023-03-01" in src.provenance["bid_missing_periods"]  # 404 recorded, never filled
    assert (bars["high"] >= bars[["open", "close"]].max(axis=1)).all()
    # second load comes from the cache (no fetch calls)
    src2 = DukascopyCandleSource("EURUSD", "2023-01-01", "2023-03-01", point=1e-5, cache_dir=tmp_path,
                                 fetch=lambda u: (_ for _ in ()).throw(AssertionError("network used")))
    assert len(src2.fetch_series()) > 0


def test_mt5_server_time_conversion(tmp_path):
    naive = pd.DatetimeIndex(["2024-01-15 19:00", "2024-07-15 19:00"])
    utc = server_to_utc(naive, "nyclose")
    assert list(utc.hour) == [17, 16]  # UTC+2 in winter, UTC+3 in summer
    assert server_to_utc(naive, "+02:00")[1].hour == 17
    p = tmp_path / "x.csv"
    p.write_text("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n"
                 "2024.01.15\t19:00:00\t1.09500\t1.09600\t1.09400\t1.09550\t1200\t0\t6\n")
    df = Mt5CsvSource(str(p), "nyclose", "1h", 1e-5).fetch_series()
    assert df.index[0] == pd.Timestamp("2024-01-15 18:00", tz="UTC")  # open 17:00 UTC + 1h -> close stamp
    assert df["spread"].iloc[0] == pytest.approx(6e-5)


def _intraday_and_fix(shift_hours=0, scale=1.0):
    idx = pd.date_range("2018-01-01", "2020-12-31", freq="1h", tz="UTC")
    rng = np.random.default_rng(0)
    close = 1.15 * np.exp(np.cumsum(rng.normal(0, 0.0008, len(idx))))
    bars = pd.DataFrame({"close": close}, index=idx)
    days = pd.bdate_range("2018-01-02", "2020-12-30")
    fix_t = (days + pd.Timedelta("12h")).tz_localize("America/New_York").tz_convert("UTC")
    ref = pd.Series(bars["close"].reindex(fix_t).to_numpy() * scale, index=fix_t).dropna()
    if shift_hours:
        bars.index = bars.index + pd.Timedelta(hours=shift_hours)
    return bars, ref


def test_cross_check_passes_on_aligned_data_and_catches_errors():
    bars, ref = _intraday_and_fix()
    assert cross_check_daily(bars, ref)["status"] == "PASSED"
    bars2, ref2 = _intraday_and_fix(shift_hours=1)
    with pytest.raises(DataQualityError):
        cross_check_daily(bars2, ref2)  # clock off by one hour
    bars3, ref3 = _intraday_and_fix(scale=1 / 1.15)
    with pytest.raises(DataQualityError):
        cross_check_daily(bars3, ref3)  # inverted / wrong scale


def test_observed_spread_is_charged_only_when_wider():
    n = 30
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    bars = pd.DataFrame({"open": 1.1, "high": 1.1, "low": 1.1, "close": 1.1, "volume": 1.0, "spread": 0.00001}, index=idx)
    entries = np.zeros(n, dtype=bool)
    entries[3] = True
    c = CostModel(spread_bps=1.0, commission_bps=0, slippage_bps=0)
    m = MarketArrays.from_bars(bars, 6000)
    m.vol = np.full(n, 0.001)
    narrow = run_backtest(m, entries, 1, 2, None, None, c, slice(0, n))
    assert narrow.trades["cost"].iloc[0] == pytest.approx(1e-4)  # floor applies (observed 0.09 bps < 1 bps)
    bars["spread"] = 0.00055  # 5 bps observed
    m2 = MarketArrays.from_bars(bars, 6000)
    m2.vol = np.full(n, 0.001)
    wide = run_backtest(m2, entries, 1, 2, None, None, c, slice(0, n))
    assert wide.trades["cost"].iloc[0] == pytest.approx(0.00055 / 1.1)


def test_rate_limited_downloads_back_off_and_succeed(tmp_path, monkeypatch):
    from xquant.errors import RateLimited
    monkeypatch.setattr("xquant.data.sources.dukascopy_candles.time.sleep", lambda s: None)
    blob = _blob(_hourly_rows(24 * 31))
    calls = {"n": 0}

    def fetch(url):
        calls["n"] += 1
        if calls["n"] % 2 == 1:
            raise RateLimited(url, retry_after=1)
        return blob

    src = DukascopyCandleSource("EURUSD", "2023-01-01", "2023-02-01", point=1e-5, fetch=fetch,
                                cache_dir=tmp_path, workers=1)
    assert len(src.fetch_series()) > 0 and calls["n"] >= 4


def test_failed_periods_do_not_abort_others_and_resume(tmp_path, monkeypatch):
    from xquant.errors import DataUnavailableError
    monkeypatch.setattr("xquant.data.sources.dukascopy_candles.time.sleep", lambda s: None)
    blob = _blob(_hourly_rows(24 * 28))
    down = {"2023/01/BID_candles_hour_1.bi5"}

    def fetch(url):
        key = url.split("/EURUSD/")[1]
        if key in down:
            raise DataUnavailableError("reset")
        return blob

    kw = dict(point=1e-5, cache_dir=tmp_path, workers=1, min_interval=0, retries=2)
    with pytest.raises(DataUnavailableError, match="1 period"):
        DukascopyCandleSource("EURUSD", "2023-01-01", "2023-04-01", fetch=fetch, **kw).fetch_series()
    cached = {p.name for p in (tmp_path / "dukascopy_candles" / "EURUSD" / "hour" / "BID").glob("*.bi5")}
    assert cached == {"20230101.bi5", "20230301.bi5"}  # the others were still downloaded
    down.clear()
    assert len(DukascopyCandleSource("EURUSD", "2023-01-01", "2023-04-01", fetch=fetch, **kw).fetch_series()) > 0


def test_session_aggregation_17h_new_york():
    from xquant.data.sources.resample import aggregate_sessions
    idx = pd.date_range("2024-03-04 00:00", "2024-03-16 00:00", freq="1h", tz="UTC")  # spans US DST start (Mar 10)
    idx = idx[idx.dayofweek < 5]
    n = len(idx)
    bars = pd.DataFrame({"open": np.arange(n) + 1.0, "high": np.arange(n) + 1.5, "low": np.arange(n) + 0.5,
                         "close": np.arange(n) + 1.2, "volume": 1.0, "spread": 0.0001}, index=idx)
    out, info = aggregate_sessions(bars, "17:00", "America/New_York", min_bars=12)
    local = out.index.tz_convert("America/New_York")
    assert (local.hour == 17).all()  # stamped at 17:00 New York across the DST change
    # session closing Tue 2024-03-05 17:00 NY (22:00 UTC) contains the bars closing after Mon 22:00 UTC
    d = out.loc[pd.Timestamp("2024-03-05 22:00", tz="UTC")]
    sel = bars[(bars.index > pd.Timestamp("2024-03-04 22:00", tz="UTC")) & (bars.index <= pd.Timestamp("2024-03-05 22:00", tz="UTC"))]
    assert d["open"] == sel["open"].iloc[0] and d["close"] == sel["close"].iloc[-1]
    assert d["high"] == sel["high"].max() and d["low"] == sel["low"].min()
    assert info["short_sessions_dropped"] >= 1  # partial first/last sessions are dropped, not padded


def test_monthly_mean_cross_check():
    from xquant.data.crosscheck import cross_check_monthly_mean
    idx = pd.date_range("2015-01-01", "2020-12-31 23:00", freq="1h", tz="UTC")
    rng = np.random.default_rng(1)
    bars = pd.DataFrame({"close": 1200 * np.exp(np.cumsum(rng.normal(0, 0.001, len(idx))))}, index=idx)
    ref = bars["close"].groupby(idx.tz_localize(None).to_period("M")).mean()
    ref.index = ref.index.to_timestamp()
    assert cross_check_monthly_mean(bars, ref * 1.002)["status"] == "PASSED"
    with pytest.raises(DataQualityError):
        cross_check_monthly_mean(bars * 0.1, ref)  # wrong point scaling


def test_hour_aggregation_h4_aligned_to_17h_new_york():
    from xquant.data.sources.resample import aggregate_hours
    idx = pd.date_range("2024-01-08 00:00", "2024-01-12 00:00", freq="1h", tz="UTC")
    n = len(idx)
    bars = pd.DataFrame({"open": np.arange(n) + 1.0, "high": np.arange(n) + 1.5, "low": np.arange(n) + 0.5,
                         "close": np.arange(n) + 1.2, "volume": 1.0}, index=idx)
    out, info = aggregate_hours(bars, 4)
    local = out.index.tz_convert("America/New_York")
    assert set(local.hour) <= {17, 21, 1, 5, 9, 13}
    b = out.loc[pd.Timestamp("2024-01-09 22:00", tz="UTC")]  # 17:00 NY close: hourly closes 18:00..22:00 UTC
    sel = bars[(bars.index > pd.Timestamp("2024-01-09 18:00", tz="UTC")) & (bars.index <= pd.Timestamp("2024-01-09 22:00", tz="UTC"))]
    assert b["open"] == sel["open"].iloc[0] and b["close"] == sel["close"].iloc[-1] and b["high"] == sel["high"].max()


def test_bid_only_mode_skips_ask_downloads(tmp_path):
    calls = []
    blob = _blob(_hourly_rows(24 * 31))

    def fetch(url):
        calls.append(url)
        if "/2023/00/BID" in url:
            return blob
        raise DataNotFound(url)

    src = DukascopyCandleSource("EURUSD", "2023-01-01", "2023-02-01", point=1e-5, min_interval=0, fetch=fetch,
                                cache_dir=tmp_path, sides=["BID"])
    bars = src.fetch_series()
    assert len(bars) > 600 and bars["spread"].isna().all()
    assert not any("ASK" in u for u in calls)
    with pytest.raises(Exception, match="sides"):
        DukascopyCandleSource("EURUSD", "2023-01-01", "2023-02-01", sides=["ASK"])
