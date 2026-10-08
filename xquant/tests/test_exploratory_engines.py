import numpy as np
import pandas as pd
import pytest

from tests.conftest import default_splits, synthetic_dataset
from xquant.findings import Finding, apply_fdr
from xquant.macro.engine import MacroEngine
from xquant.macro.event_study import event_study
from xquant.macro.expectation import MIN_HISTORY, compute_surprises
from xquant.market.behavior import MarketBehaviorEngine
from xquant.news.engine import KeywordNewsClassifier, NewsEngine
from xquant.stats import (
    benjamini_hochberg,
    deflated_sharpe,
    hac_conditional_diff,
    variance_ratio_test,
    wilson_interval,
)


def test_bh_fdr_matches_reference():
    p = [0.01, 0.04, 0.03, 0.005, 0.5]
    rej, q = benjamini_hochberg(p, 0.05)
    assert list(rej) == [True, True, True, True, False]
    assert q[3] == pytest.approx(0.025)


def test_variance_ratio_detects_autocorrelation_and_not_noise():
    rng = np.random.default_rng(0)
    noise = rng.normal(size=4000)
    assert variance_ratio_test(noise, 5).p_value > 0.01
    ar = np.zeros(4000)
    for t in range(1, 4000):
        ar[t] = 0.2 * ar[t - 1] + noise[t]
    res = variance_ratio_test(ar, 5)
    assert res.p_value < 1e-6 and res.effect > 1


def test_hac_conditional_diff_and_wilson():
    rng = np.random.default_rng(1)
    y = rng.normal(size=3000)
    c = rng.random(3000) < 0.2
    assert hac_conditional_diff(y, c).p_value > 0.01
    y2 = y + 0.3 * c
    assert hac_conditional_diff(y2, c).p_value < 1e-6
    lo, hi = wilson_interval(57, 100)
    assert lo < 0.57 < hi


def test_deflated_sharpe_penalises_many_trials():
    rng = np.random.default_rng(2)
    r = rng.normal(0.0005, 0.01, 2000)
    assert deflated_sharpe(r, 1, 0.0) > deflated_sharpe(r, 5000, 0.001)


def test_market_engine_finds_nothing_in_random_walk(random_walk_ds):
    ds = random_walk_ds
    eng = MarketBehaviorEngine(ds, default_splits(ds), [1, 5, 10, 20], seed=0)
    found = eng.run()
    discoveries = [f for f in found if f.status == "DISCOVERY"]
    assert discoveries == [], [f.name for f in discoveries]
    assert any(f.status == "INSUFFICIENT DATA" and f.name == "hour_of_day" for f in found)


def test_market_engine_detects_injected_momentum(momentum_ds):
    ds = momentum_ds
    found = MarketBehaviorEngine(ds, default_splits(ds), [1, 5, 10, 20], seed=0).run()
    names = {f.name for f in found if f.status == "DISCOVERY"}
    assert "variance_ratio_q2" in names


def _calendar(close_index: pd.DatetimeIndex, n: int, rng: np.random.Generator) -> pd.DataFrame:
    pos = np.sort(rng.choice(np.arange(30, len(close_index) - 30), size=n, replace=False))
    ts = close_index[pos] - pd.Timedelta("2h")  # release 2h before the bar close
    consensus = rng.normal(2.0, 0.3, n)
    actual = consensus + rng.normal(0, 0.2, n)
    return pd.DataFrame({"event": "CPI", "country": "US", "currency": "USD", "importance": 3,
                         "previous": consensus, "consensus": consensus, "actual": actual},
                        index=pd.DatetimeIndex(ts, name="timestamp"))


def test_expectation_engine_standardises_with_past_only():
    rng = np.random.default_rng(3)
    idx = pd.date_range("2010-01-01", periods=40, freq="MS", tz="UTC")
    ev = pd.DataFrame({"event": "CPI", "previous": 1.0, "consensus": 2.0, "actual": 2.0 + rng.normal(0, 0.1, 40)}, index=idx)
    out = compute_surprises(ev)
    assert out["std_surprise"].iloc[:MIN_HISTORY].isna().all()
    k = 20
    expected = out["surprise"].iloc[k] / out["surprise"].iloc[:k].std()
    assert out["std_surprise"].iloc[k] == pytest.approx(expected)
    ev.loc[idx[5], "consensus"] = np.nan
    assert np.isnan(compute_surprises(ev)["surprise"].iloc[5])  # never imputed


def test_event_study_recovers_injected_surprise_effect():
    rng = np.random.default_rng(4)
    r = rng.normal(0, 0.005, 4000)
    ds = synthetic_dataset(r)
    cal = compute_surprises(_calendar(ds.bars.index, 300, rng))
    pos = ds.bars.index.searchsorted(cal.index)
    r2 = r.copy()
    r2[pos] += 0.004 * np.nan_to_num(cal["std_surprise"].to_numpy())  # injected reaction to surprise
    ds2 = synthetic_dataset(r2)
    cal.index = ds2.bars.index[pos] - pd.Timedelta("2h")
    found = event_study(cal, ds2.bars["close"], np.ones(4000, dtype=bool), "CPI", "macro", "all")
    d = {f.name: f for f in found}
    assert d["CPI_surprise_to_reaction"].p_value < 1e-6 and d["CPI_surprise_to_reaction"].effect > 0
    noise = event_study(cal, ds.bars["close"].iloc[:], np.ones(4000, dtype=bool), "CPI", "macro", "all")
    nd = {f.name: f for f in noise}
    # unaffected series: the surprise does not predict anything (with high probability)
    assert nd["CPI_surprise_to_reaction"].p_value > 0.001


def test_macro_and_news_report_insufficient_data_without_sources(random_walk_ds):
    ds = random_walk_ds
    sp = default_splits(ds)
    macro = MacroEngine(ds, sp).run()
    assert any(f.status == "INSUFFICIENT DATA" and f.name == "NFP" for f in macro)
    news = NewsEngine(ds, sp).run()
    assert news[0].status == "INSUFFICIENT DATA"


def test_news_classifier_taxonomy_and_novelty():
    idx = pd.DatetimeIndex(["2024-01-01 10:00", "2024-01-01 11:00", "2024-01-03 09:00"], tz="UTC")
    news = pd.DataFrame({"source": ["Reuters", "blog", "Reuters"],
                         "headline": ["Fed signals rate hike as inflation surges",
                                      "Fed signals rate hike as inflation surges",
                                      "Euro zone GDP growth beats forecasts"]}, index=idx)
    lab = KeywordNewsClassifier().classify(news)
    assert lab["category"].iloc[0] in {"inflation", "central_bank"}
    assert lab["novelty"].iloc[1] == pytest.approx(0.0)  # duplicate headline within 24h
    assert "EZ" in lab["countries"].iloc[2] and lab["sentiment"].iloc[2] > 0


def test_apply_fdr_only_touches_tested_findings():
    fs = [Finding("e", "c", "a", "", p_value=0.001), Finding.insufficient("e", "c", "b", "x")]
    fs[0].status = "TESTED"
    apply_fdr(fs, 0.05)
    assert fs[0].status == "SIGNIFICANT_TRAIN" and fs[1].status == "INSUFFICIENT DATA"
