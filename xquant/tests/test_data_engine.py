import json
import lzma
import struct
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from xquant.config import SplitSpec, load_config
from xquant.data.cleaning import clean_bars
from xquant.data.pit import align_point_in_time
from xquant.data.schema import validate_bars
from xquant.data.sources.base import build_source, registered_kinds
from xquant.data.sources.builtin import DukascopySource, HttpCsvSource
from xquant.errors import ConfigError, DataQualityError, DataUnavailableError, SplitAccessError
from xquant.validation.splits import SplitGuard, make_splits


def test_asset_configs_load_and_switch_without_core_changes():
    for sym in ["EURUSD", "eur/usd", "BTCUSD", "XAUUSD"]:
        cfg = load_config(sym)
        assert cfg.asset.symbol.replace("/", "") in sym.upper().replace("/", "")
    with pytest.raises(ConfigError):
        load_config("NOPE")


def test_split_spec_must_be_ordered():
    with pytest.raises(ValueError):  # pydantic ValidationError wraps the ConfigError
        SplitSpec(train_end="2020-01-01", validation_end="2019-01-01", test_end="2021-01-01")


def test_registry_has_builtin_sources():
    assert {"datahub_csv", "csv_file", "dukascopy", "fred", "econ_calendar_csv", "news_csv"} <= set(registered_kinds())


def _raw(values, start="2020-01-01"):
    idx = pd.bdate_range(start, periods=len(values))
    return pd.DataFrame({"value": values}, index=idx)


def test_clean_removes_duplicates_nonpositive_and_keeps_gaps():
    rng = np.random.default_rng(0)
    vals = list(1.1 * np.exp(np.cumsum(rng.normal(0, 0.005, 400))))
    raw = _raw(vals)
    raw = pd.concat([raw, raw.iloc[[5]]])  # exact duplicate
    raw.iloc[10, 0] = -1.0  # corrupt
    raw.iloc[20, 0] = np.nan  # missing (holiday)
    bars, rep = clean_bars(raw, tz="America/New_York", timeframe="1D", close_time="12:00")
    validate_bars(bars)
    assert rep.exact_duplicates == 1 and rep.non_positive == 1 and rep.missing_close == 1
    assert len(bars) == 398
    assert str(bars.index.tz) == "UTC" and bars.index[0].hour in (16, 17)  # noon NY in UTC
    assert bars[["open", "high", "low", "volume"]].isna().all(axis=None)  # never synthesised


def test_isolated_bad_print_removed_but_real_jump_kept():
    rng = np.random.default_rng(1)
    vals = 1.1 * np.exp(np.cumsum(rng.normal(0, 0.003, 600)))
    vals[300] *= 1.20  # bad print: reverts next bar
    vals[450:] *= 0.85  # real level shift: does not revert
    bars, rep = clean_bars(_raw(vals), tz="UTC", timeframe="1D")
    assert rep.spikes_removed == 1
    assert rep.extreme_moves_kept >= 1
    assert len(bars) == 599


def test_point_in_time_alignment_never_uses_future_values():
    monthly = pd.Series([1.0, 2.0, 3.0], index=pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01"]), name="m")
    bars = pd.date_range("2020-01-15", "2020-05-15", freq="D", tz="UTC")
    out = align_point_in_time(monthly, bars, "monthly", lag_days=35, tz="UTC")
    # January value: period ends 2020-01-31 23:59:59, +35 days -> first visible on the 2020-03-07 bar
    assert out.loc[:"2020-03-06"].isna().all()
    assert out.loc["2020-03-07":"2020-04-04"].eq(1.0).all()
    assert out.loc["2020-04-05":"2020-05-05"].eq(2.0).all()


def _csv_bytes(rows):
    return ("Date,Country,Exchange rate\n" + "\n".join(f"{d},{c},{v}" for d, c, v in rows)).encode()


def test_http_csv_orientation_inverts_only_when_anchor_confirms(tmp_path):
    rows = [("1999-01-04", "Euro", 0.8466), ("1999-01-05", "Euro", 0.85), ("1999-01-04", "Japan", 112.0)]
    src = HttpCsvSource(url="u", date_col="Date", value_col="Exchange rate", filter_col="Country",
                        filter_value="Euro", snapshot="s.csv", datasets_dir=tmp_path,
                        orientation_anchor={"date": "1999-01-04", "value": 1.1812, "tolerance": 0.002},
                        fetch=lambda url: _csv_bytes(rows))
    out = src.fetch_series()
    assert out["value"].iloc[0] == pytest.approx(1 / 0.8466)
    assert "inverted" in src.provenance["orientation"]
    assert json.loads((tmp_path / "s.meta.json").read_text())["rows"] == 2
    bad = HttpCsvSource(url="u", date_col="Date", value_col="Exchange rate", filter_col="Country",
                        filter_value="Euro", datasets_dir=tmp_path,
                        orientation_anchor={"date": "1999-01-04", "value": 1.5},
                        fetch=lambda url: _csv_bytes(rows))
    with pytest.raises(DataQualityError):
        bad.fetch_series()


def test_http_csv_falls_back_to_snapshot_and_fails_loudly_without_one(tmp_path):
    rows = [("2000-01-03", "Euro", 1.0)]
    HttpCsvSource(url="u", date_col="Date", value_col="Exchange rate", snapshot="s.csv",
                  datasets_dir=tmp_path, fetch=lambda url: _csv_bytes(rows)).fetch_series()

    def down(url):
        raise DataUnavailableError("blocked")

    src = HttpCsvSource(url="u", date_col="Date", value_col="Exchange rate", snapshot="s.csv",
                        datasets_dir=tmp_path, fetch=down)
    assert len(src.fetch_series()) == 1 and src.provenance["used_snapshot"]
    with pytest.raises(DataUnavailableError):
        HttpCsvSource(url="u", date_col="Date", value_col="Exchange rate", datasets_dir=tmp_path,
                      fetch=down).fetch_series()


def test_dukascopy_bi5_decoding_and_url():
    hour = datetime(2023, 1, 2, 10)
    recs = [(0, 107050, 107040, 1.5, 2.0), (1500, 107060, 107045, 0.5, 0.25)]
    blob = lzma.compress(b"".join(struct.pack(">IIIff", *r) for r in recs), format=lzma.FORMAT_ALONE)
    df = DukascopySource.decode_bi5(blob, hour, 1e-5)
    assert df["ask"].iloc[0] == pytest.approx(1.0705) and df["bid"].iloc[1] == pytest.approx(1.07045)
    assert df.index[1] == pd.Timestamp("2023-01-02 10:00:01.5", tz="UTC")
    src = build_source("dukascopy", {"instrument": "eurusd", "start": "2023-01-02", "end": "2023-01-03"})
    assert src.url_for(hour).endswith("/EURUSD/2023/00/02/10h_ticks.bi5")  # zero-based month


def test_splits_and_guard():
    idx = pd.bdate_range("2000-01-01", "2010-12-31", tz="UTC") + pd.Timedelta("16h")
    spec = SplitSpec(train_end="2005-12-31", validation_end="2007-12-31", test_end="2009-12-31", embargo_bars=10)
    sp = make_splits(idx, spec)
    a = sp.bounds
    assert a["validation"][0] == a["train"][1] + 10 and a["final"][1] == len(idx)
    g = SplitGuard()
    g.request("train", "optimize", "t")
    with pytest.raises(SplitAccessError):
        g.request("validation", "optimize", "t")
    g.request("test", "evaluate", "t")
    with pytest.raises(SplitAccessError):
        g.request("train", "optimize", "t")  # frozen after TEST
    g.request("final", "evaluate", "t")
    with pytest.raises(SplitAccessError):
        g.request("final", "evaluate", "t")


def test_real_spike_and_reversal_with_ohlc_is_kept_but_unconfirmed_print_removed():
    """Real data shape of EUR/USD on NFP day 2007-10-05: a ~70 pip drop fully reversed next hour."""
    rng = np.random.default_rng(3)
    n = 600
    close = 1.41 * np.exp(np.cumsum(rng.normal(0, 0.0004, n)))
    open_ = np.r_[close[0], close[:-1]]
    high, low = np.maximum(open_, close) * 1.0002, np.minimum(open_, close) * 0.9998
    idx = pd.date_range("2007-09-01", periods=n, freq="1h")
    t = 400
    base = close[t - 1]
    close[t], low[t], high[t] = base * 0.9951, base * 0.9930, base * 1.0005  # NFP drop
    open_[t + 1], low[t + 1] = close[t], close[t] * 0.9998                  # next bar opens there...
    close[t + 1], high[t + 1] = base * 1.0003, base * 1.0010                # ...and reverses fully
    raw = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1.0}, index=idx)
    bars, rep = clean_bars(raw, tz="UTC", timeframe="1h")
    assert rep.spikes_removed == 0 and len(bars) == n  # real market move kept
    bad = raw.copy()
    bad.iloc[t + 1, bad.columns.get_loc("open")] = base  # next open does NOT confirm the low close
    bad.iloc[t, bad.columns.get_loc("low")] = base * 0.9930
    bars2, rep2 = clean_bars(bad, tz="UTC", timeframe="1h")
    assert rep2.spikes_removed == 1


def test_bar_frequency_exogenous_is_usable_from_its_own_close():
    idx = pd.date_range("2024-01-02 10:00", periods=6, freq="1h", tz="UTC")
    other = pd.Series([1.0, 2, 3, 4, 5, 6], index=idx.tz_localize(None), name="x")
    out = align_point_in_time(other, idx, "bar", lag_days=0, tz="UTC")
    assert list(out) == [1.0, 2, 3, 4, 5, 6]  # value stamped at bar close t is visible at t, never earlier
    shifted = align_point_in_time(other, idx - pd.Timedelta(minutes=1), "bar", lag_days=0, tz="UTC")
    assert shifted.iloc[0] != shifted.iloc[0] and list(shifted.iloc[1:]) == [1.0, 2, 3, 4, 5]
