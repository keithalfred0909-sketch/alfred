"""Opening-range breakout engine: timing, stops/targets, gaps, sizing, no-trade rules and study controls."""

import numpy as np
import pandas as pd
import pytest

from xquant.daytrade.orb import OrbParams, run_orb
from xquant.daytrade.study import DayTradeStudy
from xquant.errors import ConfigError
from xquant.memory.store import ResearchMemory


def _day(date: str, path: list[tuple[str, float, float, float, float]], fill: float) -> pd.DataFrame:
    """Minute bars (stamped at close, NY) 09:31..16:00; ``path`` overrides specific stamps with OHLC."""
    stamps = pd.date_range(f"{date} 09:31", f"{date} 16:00", freq="1min", tz="America/New_York")
    df = pd.DataFrame({"open": fill, "high": fill, "low": fill, "close": fill, "volume": 10.0}, index=stamps)
    for hm, o, h, lo, c in path:
        df.loc[pd.Timestamp(f"{date} {hm}", tz="America/New_York"), ["open", "high", "low", "close"]] = [o, h, lo, c]
    return df


def _bull_open(date: str, after: list[tuple[str, float, float, float, float]], fill: float = 101.0) -> pd.DataFrame:
    # opening candle 09:30-09:35: open 100, high 101, low 99, close 100.8 (bullish body 0.8 of range 2)
    rng = [("09:31", 100.0, 100.5, 99.0, 100.2), ("09:32", 100.2, 100.6, 99.5, 100.4),
           ("09:33", 100.4, 101.0, 100.0, 100.6), ("09:34", 100.6, 100.9, 100.3, 100.7),
           ("09:35", 100.7, 100.9, 100.5, 100.8)]
    return _day(date, rng + after, fill)


P0 = OrbParams(cost_per_fill_frac=0.0, min_stop_frac=0.0)


def test_entry_at_0935_open_stop_at_candle_low_and_eod_exit():
    bars = _bull_open("2024-03-12", [("09:36", 101.0, 101.2, 100.9, 101.1)], fill=101.5)
    t = run_orb(bars, P0)
    assert len(t) == 1
    r = t.iloc[0]
    assert r["side"] == 1 and r["entry"] == 101.0 and r["stop"] == 99.0  # entry = open of the bar stamped 09:36
    assert r["entry_time"] == pd.Timestamp("2024-03-12 09:36", tz="America/New_York")
    assert r["reason"] == "eod" and r["exit"] == 101.5 and r["r_gross"] == pytest.approx(0.5 / 2.0)


def test_stop_and_gap_through_stop():
    t = run_orb(_bull_open("2024-03-12", [("09:36", 101.0, 101.0, 100.0, 100.5), ("10:00", 100.5, 100.5, 98.5, 99.5)],
                           fill=100.5), P0)
    assert t.iloc[0]["reason"] == "stop" and t.iloc[0]["exit"] == 99.0 and t.iloc[0]["r_gross"] == pytest.approx(-1.0)
    t = run_orb(_bull_open("2024-03-12", [("09:36", 101.0, 101.0, 100.0, 100.5), ("10:00", 98.0, 98.2, 97.5, 98.0)],
                           fill=100.5), P0)
    assert t.iloc[0]["exit"] == 98.0 and t.iloc[0]["r_gross"] == pytest.approx(-1.5)  # gapped: filled at the open


def test_target_and_same_minute_stop_first():
    p = OrbParams(cost_per_fill_frac=0.0, min_stop_frac=0.0, target_r=2.0)  # target = 101 + 2*2 = 105
    t = run_orb(_bull_open("2024-03-12", [("11:00", 101.0, 105.5, 100.5, 105.0)], fill=101.0), p)
    assert t.iloc[0]["reason"] == "target" and t.iloc[0]["r_gross"] == pytest.approx(2.0)
    t = run_orb(_bull_open("2024-03-12", [("11:00", 101.0, 105.5, 98.0, 102.0)], fill=101.0), p)
    assert t.iloc[0]["reason"] == "stop"  # both touched in the same minute: assume the stop


def test_no_trade_rules_and_sizing():
    doji = _day("2024-03-12", [("09:31", 100.0, 101.0, 99.0, 100.0), ("09:35", 100.0, 100.2, 99.8, 100.05)], 100.0)
    assert run_orb(doji, P0).empty  # body 0.05 < 10% of range 2
    missing = _bull_open("2024-03-12", []).drop(pd.Timestamp("2024-03-12 16:00", tz="America/New_York"))
    assert run_orb(missing, P0).empty  # no 16:00 bar -> no trade
    tight = _bull_open("2024-03-12", [])
    assert run_orb(tight, OrbParams(min_stop_frac=0.05)).empty  # stop 2% < 5% minimum
    t = run_orb(_bull_open("2024-03-12", []), OrbParams(cost_per_fill_frac=1e-4, min_stop_frac=0.0))
    r = t.iloc[0]
    assert r["notional_x"] == pytest.approx(min(0.01 / (2 / 101), 4.0))
    assert r["risk_frac"] == pytest.approx(0.01) and r["cost_r"] == pytest.approx(2 * 1e-4 * 101 / 2)


def _synthetic_minutes(n_days: int, seed: int, drift: float = 0.0) -> pd.DataFrame:
    """Random-walk minute bars for NY sessions; optional drift after 09:35 in the direction of the opening candle."""
    rng = np.random.default_rng(seed)
    frames, px = [], 15000.0
    for d in pd.bdate_range("2017-01-02", periods=n_days):
        stamps = pd.date_range(f"{d.date()} 09:31", f"{d.date()} 16:00", freq="1min", tz="America/New_York")
        r = rng.normal(0, 0.0004, len(stamps))
        open_dir = np.sign(r[:5].sum())
        r[5:] += drift * open_dir
        c = px * np.exp(np.cumsum(r))
        o = np.r_[px, c[:-1]]
        hi, lo = np.maximum(o, c) * (1 + 0.0001), np.minimum(o, c) * (1 - 0.0001)
        frames.append(pd.DataFrame({"open": o, "high": hi, "low": lo, "close": c, "volume": 5.0}, index=stamps))
        px = c[-1]
    return pd.concat(frames).tz_convert("UTC")


def _spec(name):
    return {"name": name, "variants": [{"id": "A", "context": "none"}],
            "9_backtest": {"splits": {"train_end": "2018-12-31", "validation_end": "2019-12-31", "test_end": "2020-06-30"}}}


@pytest.mark.slow
def test_study_controls(tmp_path):
    mem = ResearchMemory(tmp_path / "m.db")
    noise = DayTradeStudy(_spec("noise"), mem, bars=_synthetic_minutes(1000, 1), reps=300, random_dir_reps=40).run()
    assert noise["verdict"] == "NO EDGE FOUND" and not noise["split_access"]
    with pytest.raises(ConfigError, match="already evaluated"):
        DayTradeStudy(_spec("noise"), mem, bars=_synthetic_minutes(1000, 1)).run()
    edge = DayTradeStudy(_spec("edge"), mem, bars=_synthetic_minutes(1000, 2, drift=0.00004), reps=300,
                         random_dir_reps=40).run()
    assert edge["verdict"] == "EDGE FOUND (provisional)", [(r["status"], r["checks"]) for r in edge["results"]]
