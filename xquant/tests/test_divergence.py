import numpy as np
import pandas as pd
import pytest

from tests.test_intraday_sources import _blob, _hourly_rows
from xquant.data.sources.basket import DXY_COMPONENTS, DXY_CONSTANT, BasketSource, combine
from xquant.errors import DataNotFound
from xquant.features.discovery import FeaturePool
from xquant.features.library import assert_causal, build_primitives, divergence_features, is_categorical, prim


def test_combine_is_geometric_and_drops_incomplete_timestamps():
    idx = pd.date_range("2024-01-01", periods=4, freq="1h", tz="UTC")
    a = pd.Series([1.10, 1.12, 1.08, 1.05], index=idx)
    b = pd.Series([150.0, 151.0, 149.0], index=idx[[0, 1, 3]])  # no bar at idx[2]
    out, dropped = combine({"A": a, "B": b}, {"A": -0.5, "B": 0.25}, 2.0)
    assert dropped == 1 and list(out.index) == list(idx[[0, 1, 3]])  # never forward-filled
    assert out.iloc[0] == pytest.approx(2.0 * 1.10 ** -0.5 * 150.0 ** 0.25)


def test_dxy_formula_identities():
    # all pairs at 1.0 -> the constant; +1% EURUSD -> DXY falls by its 57.6% weight (log terms)
    ones = {c["instrument"]: 1.0 for c in DXY_COMPONENTS}
    lvl = lambda px: DXY_CONSTANT * np.prod([px[c["instrument"]] ** c["exponent"] for c in DXY_COMPONENTS])  # noqa: E731
    assert lvl(ones) == pytest.approx(DXY_CONSTANT)
    assert np.log(lvl({**ones, "EURUSD": 1.01}) / lvl(ones)) == pytest.approx(-0.576 * np.log(1.01))
    assert sum(abs(c["exponent"]) for c in DXY_COMPONENTS) == pytest.approx(1.0)


def test_basket_source_ex_eur_renormalises_and_uses_component_sources(tmp_path):
    files = {}
    for inst, base in [("USDJPY", 140000), ("GBPUSD", 126000), ("USDCAD", 133000), ("USDSEK", 1020000),
                       ("USDCHF", 85000)]:
        files[f"{inst}/2023/00/BID_candles_hour_1.bi5"] = _blob(_hourly_rows(24 * 31, base=base, seed=len(inst)))
        files[f"{inst}/2023/00/ASK_candles_hour_1.bi5"] = _blob(_hourly_rows(24 * 31, base=base, spread=5,
                                                                             seed=len(inst)))

    def fetch(url):
        key = url.split("/datafeed/")[1]
        if key not in files:
            raise DataNotFound(url)
        return files[key]
    comps = [dict(c) for c in DXY_COMPONENTS]
    for c in comps:
        c["point"] = 1e-3 if c["instrument"] == "USDJPY" else 1e-5
    src = BasketSource(comps, drop=["EURUSD"], renormalize=True, start="2023-01-01", end="2023-02-01",
                       granularity="hour", fetch=fetch, cache_dir=tmp_path, min_interval=0)
    assert sum(abs(c["exponent"]) for c in src.comps) == pytest.approx(1.0)
    assert "EURUSD" not in {c["instrument"] for c in src.comps}
    out = src.fetch_series()
    assert {"close", "value"} <= set(out.columns) and len(out) > 600
    assert src.provenance["bars"] == len(out) and src.provenance["constant"] == 1.0


def _pair(n=1500, seed=3):
    """EURUSD-like asset and an inverse dollar index driven by the same factor plus noise."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-02", periods=n, freq="1h", tz="UTC")
    f = rng.normal(0, 0.001, n)
    la = pd.Series(np.cumsum(f + rng.normal(0, 0.0004, n)) + np.log(1.1), index=idx)
    lx = pd.Series(np.cumsum(-0.6 * f + rng.normal(0, 0.0003, n)) + np.log(100), index=idx)
    return la, lx


def test_divergence_features_are_causal_and_detect_inverse_relationship():
    la, lx = _pair()
    bars = pd.DataFrame({"open": np.exp(la), "high": np.exp(la) * 1.0005, "low": np.exp(la) * 0.9995,
                         "close": np.exp(la), "volume": 1.0}, index=la.index)
    exog = pd.DataFrame({"px_dxy": np.exp(lx)}, index=la.index)
    P = build_primitives(bars, exog, "America/New_York")
    names = [f"x_px_dxy_div{k}" for k in (1, 5, 20)] + ["x_px_dxy_smt20", "x_px_dxy_smt60"]
    assert set(names) <= set(P)
    for name in names:
        assert P[name].notna().sum() > 500, name
        assert_causal(lambda b, n=name: build_primitives(b, exog.loc[b.index], "America/New_York")[n], bars,
                      [700, 1100, 1499], name)
    assert set(P["x_px_dxy_smt20"].dropna().unique()) <= {-1.0, 0.0, 1.0}
    # the residual removes the common factor: much less correlated with the dollar move than the raw return
    ret5 = la.diff(5)
    assert abs(P["x_px_dxy_div5"].corr(lx.diff(5))) < 0.5 * abs(ret5.corr(lx.diff(5)))


def test_smt_signs_on_a_constructed_example():
    idx = pd.date_range("2023-01-02", periods=700, freq="1h", tz="UTC")
    rng = np.random.default_rng(1)
    f = rng.normal(0, 0.001, 700)
    la = pd.Series(np.cumsum(f), index=idx)
    lx = pd.Series(np.cumsum(-f) + rng.normal(0, 1e-5, 700), index=idx)  # inverse pair
    t = 650
    la.iloc[t] = la.iloc[t - 20:t].min() - 0.01  # asset breaks its 20-bar low ...
    lx.iloc[t] = lx.iloc[t - 20:t].max() - 0.01  # ... the inverse series does NOT break its high -> bullish SMT
    out = divergence_features(la, lx, "px_dxy")
    assert out["x_px_dxy_smt20"].iloc[t] == 1.0
    lx.iloc[t] = lx.iloc[t - 20:t].max() + 0.01  # now it confirms -> no divergence
    assert divergence_features(la, lx, "px_dxy")["x_px_dxy_smt20"].iloc[t] == 0.0


def test_categorical_detection_and_focus_ordering():
    assert is_categorical("hour") and is_categorical("x_px_dxy_smt20")
    assert not is_categorical("x_px_dxy_div5") and not is_categorical("zscore(x_px_dxy_smt20,20)")
    exprs = {k: prim(k) for k in ["ret_1", "vol_20", "x_vix", "x_px_dxy_div5", "x_px_dxy_smt20"]}
    pool = FeaturePool(exprs=exprs, scores=[], confirmed=["vol_20"], inner_split=(slice(0, 1), slice(1, 2)))
    assert pool.hypothesis_features(3) == ["vol_20", "ret_1", "x_vix"]
    assert pool.hypothesis_features(3, ["x_px_"]) == ["x_px_dxy_div5", "x_px_dxy_smt20", "vol_20"]
