"""Walk-forward ML study: no use of the prediction year in training, and positive / negative controls."""

import numpy as np
import pandas as pd
import pytest

from tests.conftest import synthetic_dataset
from tests.test_integration import _edge_returns
from xquant.config import load_config
from xquant.memory.store import ResearchMemory
from xquant.ml.walkforward import MLStudy, walk_forward_predictions


def test_predictions_only_use_earlier_years():
    rng = np.random.default_rng(0)
    n = 3000
    idx = pd.bdate_range("2010-01-01", periods=n)
    X = pd.DataFrame({"a": rng.normal(size=n)}, index=idx)
    y = pd.Series((rng.random(n) > 0.5).astype(float), index=idx)
    years = np.asarray(idx.year)
    params = {"max_depth": 2, "max_iter": 20, "random_state": 0}
    base = walk_forward_predictions(X, y, years, 6, params, 2014)
    y2 = y.copy()
    y2[idx.year >= 2016] = 1 - y2[idx.year >= 2016]  # change the future only
    alt = walk_forward_predictions(X, y2, years, 6, params, 2014)
    early = idx.year <= 2016  # 2016 predictions come from a model fitted on data ending 6 bars before 2016
    np.testing.assert_allclose(base["p"][early].dropna(), alt["p"][early].dropna())
    assert base["p"][idx.year < 2014].isna().all()


def _cfg(ds, symbol):
    idx = ds.bars.index
    n = len(idx)
    return load_config("EURUSD", overrides={"asset": {"symbol": symbol, "macro": [], "cross_assets": [],
                                                      "splits": {"train_end": str(idx[int(n * 0.55)].date()),
                                                                 "validation_end": str(idx[int(n * 0.72)].date()),
                                                                 "test_end": str(idx[int(n * 0.86)].date()),
                                                                 "embargo_bars": 20}}})


@pytest.mark.slow
def test_controls(tmp_path):
    # hourly-like sample size: with ~5,000 bars the injected effect gives too few trades to be detectable
    noise = synthetic_dataset(np.random.default_rng(99).normal(0, 0.006, 30000), start="1900-01-01")
    edge = synthetic_dataset(_edge_returns(30000, seed=5), start="1900-01-01")
    spec = {"name": "ml_ctrl", "assets": ["NOISE", "EDGE"],
            "model": {"max_depth": 3, "learning_rate": 0.05, "max_iter": 100, "random_state": 0}}
    data = {"NOISE": (noise.bars, noise.exog, _cfg(noise, "NOISE")), "EDGE": (edge.bars, edge.exog, _cfg(edge, "EDGE"))}
    out = MLStudy(spec, ResearchMemory(tmp_path / "m.db"), datasets=data, reps=200).run()
    res = {r["asset"]: r for r in out["results"]}
    assert res["NOISE"]["status"] == "REJECTED"
    assert res["EDGE"]["status"] == "ROBUST" and res["EDGE"]["sharpe_ci"][0] > 0
