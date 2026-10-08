"""Allocation engine: causality, timing, costs, and positive/negative controls of the full study."""

import numpy as np
import pandas as pd
import pytest

from xquant.allocation import rules
from xquant.allocation.study import AllocationStudy, portfolio_returns
from xquant.errors import ConfigError
from xquant.memory.store import ResearchMemory


def _panel(n=3000, k=4, seed=0, momentum=0.0):
    """Daily closes at 17:00 NY; optional injected time-series momentum (drift = sign of the past 63 days)."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2008-01-01", periods=n, tz="America/New_York") + pd.Timedelta(hours=17)
    r = rng.normal(0, 0.008, (n, k))
    for t in range(64, n):
        r[t] += momentum * np.sign(r[t - 63:t].sum(axis=0))
    closes = pd.DataFrame(100 * np.exp(np.cumsum(r, axis=0)), index=idx.tz_convert("UTC"),
                          columns=[f"A{i}" for i in range(k)])
    return closes


def _spec(kind="tsmom", name="t1", universe=None, variants=None):
    universe = universe or ["A0", "A1", "A2", "A3"]
    return {"name": name, "kind": kind, "hypothesis": "h", "universe": universe,
            "variants": variants or [{"lookback": 63}],
            "costs_bps_per_unit_turnover": {u: 1.0 for u in universe},
            "splits": {"train_end": "2014-12-31", "validation_end": "2016-12-31", "test_end": "2018-12-31"}}


def test_rules_are_causal():
    closes = _panel(1500)
    cut = 1100
    full_t, trunc_t = rules.tsmom(closes, 63), rules.tsmom(closes.iloc[:cut], 63)
    pd.testing.assert_frame_equal(full_t.iloc[:cut - 1], trunc_t.iloc[:cut - 1])  # the last row may be a month end
    full_x, trunc_x = rules.xs_momentum(closes, 20), rules.xs_momentum(closes.iloc[:cut], 20)
    pd.testing.assert_frame_equal(full_x.iloc[:cut - 1], trunc_x.iloc[:cut - 1])
    r = closes["A0"].pct_change()
    train = pd.Series(np.arange(len(r)) < 800, index=r.index)
    w_full, _ = rules.vol_managed(r, None, "daily", 22, 2.0, train)
    w_trunc, _ = rules.vol_managed(r.iloc[:cut], None, "daily", 22, 2.0, train.iloc[:cut])
    pd.testing.assert_series_equal(w_full.iloc[:cut], w_trunc)
    assert w_full[train].mean() == pytest.approx(1.0, rel=1e-6) and w_full.max() <= 2.0


def test_weights_change_only_on_rebalance_days_and_xs_is_dollar_neutral():
    closes = _panel(800)
    w = rules.tsmom(closes, 63)
    local = w.index.tz_convert("America/New_York")
    changed = w.diff().abs().sum(axis=1) > 0
    month_end = pd.Series(local.month, index=w.index) != pd.Series(local.month, index=w.index).shift(-1)
    assert (changed[1:] <= month_end.shift(1, fill_value=False)[1:] | month_end[1:]).all()
    x = rules.xs_momentum(closes, 20)
    active = x.abs().sum(axis=1) > 0
    assert np.allclose(x[active].sum(axis=1), 0.0) and np.allclose(x[active].abs().sum(axis=1), 2.0)


def test_weights_apply_to_next_day_and_costs_follow_turnover():
    idx = pd.date_range("2024-01-01", periods=4, freq="D", tz="UTC")
    rets = pd.DataFrame({"A": [0.0, 0.01, 0.02, -0.01]}, index=idx)
    w = pd.DataFrame({"A": [0.0, 1.0, 1.0, 0.0]}, index=idx)
    pr = portfolio_returns(w, rets, {"A": 10.0})
    assert pr["gross"].tolist() == pytest.approx([0.0, 0.0, 0.02, -0.01])  # day-1 weight earns day-2 return
    assert pr["cost"].tolist() == pytest.approx([0.0, 0.0, 1e-3, 0.0])  # entry at close of day 1, charged day 2


@pytest.mark.slow
def test_negative_control_noise_is_rejected(tmp_path):
    closes = _panel(3000, seed=3)
    mem = ResearchMemory(tmp_path / "m.db")
    out = AllocationStudy(_spec(), mem, panel=(closes, {}), reps=300).run()
    assert out["verdict"] == "NO EDGE FOUND"
    assert all(r["status"] == "REJECTED" for r in out["results"]) and not out["split_access"]
    with pytest.raises(ConfigError, match="already evaluated"):
        AllocationStudy(_spec(), mem, panel=(closes, {}), reps=300).run()


@pytest.mark.slow
def test_positive_control_injected_momentum_is_found(tmp_path):
    closes = _panel(3000, seed=4, momentum=0.0012)
    out = AllocationStudy(_spec(name="t2"), ResearchMemory(tmp_path / "m.db"), panel=(closes, {}), reps=300).run()
    assert out["verdict"] == "EDGE FOUND (provisional)", [(r["status"], r["checks"]) for r in out["results"]]
    assert {e["split"] for e in out["split_access"]} == {"test", "final"}


def test_vol_managed_study_compares_with_buy_and_hold(tmp_path):
    closes = _panel(3000, k=1, seed=5)[["A0"]]
    spec = _spec(kind="vol_managed", name="v1", universe=["A0"], variants=[{"rv": "daily", "window": 22, "cap": 2.0}])
    out = AllocationStudy(spec, ResearchMemory(tmp_path / "m.db"), panel=(closes, {}), reps=200).run()
    r = out["results"][0]
    assert "benchmark_primary" in r and "beats_benchmark" in r["checks"]
    assert r["avg_exposure"] == pytest.approx(1.0, abs=0.15)
