import numpy as np
import pandas as pd
import pytest

from tests.conftest import synthetic_dataset
from xquant.backtest.engine import MarketArrays, run_backtest
from xquant.backtest.metrics import compute_metrics
from xquant.config import CostModel
from xquant.features.library import assert_causal, build_primitives, evaluate, parse_key, prim, random_expr
from xquant.strategy.genome import Condition, Genome, entry_signal, fit_thresholds, neighbours

ZERO = CostModel(spread_bps=0, commission_bps=0, slippage_bps=0)


def _arrays(close, ohlc=None):
    idx = pd.bdate_range("2020-01-01", periods=len(close), tz="UTC")
    bars = pd.DataFrame({"open": np.nan, "high": np.nan, "low": np.nan, "close": close, "volume": np.nan}, index=idx)
    if ohlc is not None:
        bars[["open", "high", "low"]] = ohlc
    m = MarketArrays.from_bars(bars, 252)
    m.vol = np.full(len(close), 0.01)
    return m


def test_fill_is_next_bar_and_returns_add_up():
    close = np.exp(np.cumsum(np.r_[0, np.full(29, 0.01)]))
    m = _arrays(close)
    entries = np.zeros(30, dtype=bool)
    entries[5] = True
    res = run_backtest(m, entries, 1, 3, None, None, ZERO, slice(0, 30))
    t = res.trades.iloc[0]
    assert t.entry_i == 6 and t.exit_i == 9  # signal at 5 -> fill at close 6 -> 3 bars
    assert t.gross == pytest.approx(0.03)
    assert res.returns.sum() == pytest.approx(t.net)


def test_costs_charged_per_fill_and_stress():
    close = np.ones(30) * 1.1
    m = _arrays(close)
    entries = np.zeros(30, dtype=bool)
    entries[[2, 10]] = True
    c = CostModel(spread_bps=1.0, commission_bps=0.5, slippage_bps=0.5)
    res = run_backtest(m, entries, 1, 2, None, None, c, slice(0, 30))
    assert len(res.trades) == 2
    assert res.trades["net"].iloc[0] == pytest.approx(-2 * 1.5e-4)
    stressed = run_backtest(m, entries, 1, 2, None, None, c, slice(0, 30), cost_mult=2.0)
    assert stressed.returns.sum() < res.returns.sum()


def test_stop_is_pessimistic_when_both_levels_hit_intrabar():
    n = 20
    close = np.full(n, 100.0)
    ohlc = np.column_stack([np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.0)])
    ohlc[7] = [100.0, 110.0, 90.0]  # huge range bar: both stop and take reachable
    m = _arrays(close, ohlc)
    entries = np.zeros(n, dtype=bool)
    entries[5] = True
    res = run_backtest(m, entries, 1, 5, 1.0, 1.0, ZERO, slice(0, n))
    assert res.trades["reason"].iloc[0] == "stop" and res.trades["net"].iloc[0] < 0


def test_no_overlapping_positions_and_window_respected():
    close = np.exp(np.cumsum(np.full(100, 0.001)))
    m = _arrays(close)
    entries = np.ones(100, dtype=bool)
    res = run_backtest(m, entries, 1, 5, None, None, ZERO, slice(20, 60))
    ent = res.trades["entry_i"].to_numpy()
    ex = res.trades["exit_i"].to_numpy()
    assert (ent[1:] > ex[:-1]).all() and ent.min() > 20 and ex.max() <= 59


def test_metrics_basic():
    r = np.r_[np.full(126, 0.001), np.full(126, -0.0005)]
    met = compute_metrics(r, np.array([0.01, -0.005, 0.02]), np.ones(252, bool), 252)
    assert met.trades == 3 and met.profit_factor == pytest.approx(6.0)
    assert 0 < met.max_drawdown < 0.07 and met.win_rate == pytest.approx(2 / 3)


def test_all_primitives_and_random_expressions_are_causal():
    rng = np.random.default_rng(0)
    ds = synthetic_dataset(rng.normal(0, 0.006, 700))
    exog = pd.DataFrame({"m": np.cumsum(rng.normal(size=700))}, index=ds.bars.index)
    cuts = [300, 450, 699]
    names = list(build_primitives(ds.bars, exog).keys())
    for name in names:
        assert_causal(lambda b, n=name: build_primitives(b, exog.loc[b.index])[n], ds.bars, cuts, name)
    for _ in range(15):
        e = random_expr(rng, names, 4)
        assert parse_key(e.key()).key() == e.key()
        assert_causal(lambda b, e=e: evaluate(e, build_primitives(b, exog.loc[b.index])), ds.bars, cuts, e.key())


def test_lookahead_guard_catches_future_leak():
    from xquant.errors import LookAheadError
    rng = np.random.default_rng(0)
    ds = synthetic_dataset(rng.normal(0, 0.006, 400))
    with pytest.raises(LookAheadError):
        assert_causal(lambda b: b["close"].shift(-1), ds.bars, [100, 200], "leaky")
    with pytest.raises(LookAheadError):  # full-sample normalisation is a classic leak
        assert_causal(lambda b: (b["close"] - b["close"].mean()) / b["close"].std(), ds.bars, [100], "zfull")


def test_genome_signal_thresholds_and_neighbours():
    rng = np.random.default_rng(1)
    ds = synthetic_dataset(rng.normal(0, 0.006, 600))
    P = build_primitives(ds.bars, None)
    g = Genome((Condition("ret_5", "low", 0.1),), 1, 5, stop=1.0)
    fs = fit_thresholds(g, P, slice(0, 400))
    sig = entry_signal(fs, P, None)
    rate = sig[:400][np.isfinite(P["ret_5"].to_numpy()[:400])].mean()
    assert 0.08 < rate < 0.12
    nb = neighbours(g)
    assert len(nb) >= 4 and all(n.key() != g.key() for n in nb)
    assert prim("ret_5").complexity == 1 and g.complexity == 2
