"""Shared fixtures. Synthetic series are used ONLY to verify that the lab's statistics behave correctly
(false-positive control on noise, detection of injected effects). They are never presented as market data."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from xquant.config import SplitSpec
from xquant.data.cleaning import QualityReport
from xquant.data.engine import MarketDataset
from xquant.data.schema import DatasetMeta, frame_sha256, infer_capabilities
from xquant.validation.splits import make_splits


def synthetic_dataset(returns: np.ndarray, start: str = "2000-01-03", exog: pd.DataFrame | None = None,
                      symbol: str = "SYN") -> MarketDataset:
    idx = pd.bdate_range(start, periods=len(returns), tz="UTC") + pd.Timedelta("16h")
    close = 1.2 * np.exp(np.cumsum(returns))
    bars = pd.DataFrame({"open": np.nan, "high": np.nan, "low": np.nan, "close": close, "volume": np.nan},
                        index=pd.DatetimeIndex(idx, name="timestamp"))
    meta = DatasetMeta(symbol=symbol, timeframe="1D", source="synthetic-test", sha256=frame_sha256(bars),
                       capabilities=infer_capabilities(bars, "1D"), n_rows=len(bars), start=str(idx[0]),
                       end=str(idx[-1]))
    ds = MarketDataset(bars=bars, meta=meta, quality=QualityReport(rows_in=len(bars), rows_out=len(bars)))
    ds.exog = exog if exog is not None else pd.DataFrame(index=bars.index)
    return ds


def default_splits(ds: MarketDataset):
    n = len(ds.bars)
    idx = ds.bars.index
    spec = SplitSpec(train_end=idx[int(n * 0.55)].date(), validation_end=idx[int(n * 0.70)].date(),
                     test_end=idx[int(n * 0.85)].date(), embargo_bars=20)
    return make_splits(idx, spec)


@pytest.fixture
def random_walk_ds() -> MarketDataset:
    rng = np.random.default_rng(12345)
    return synthetic_dataset(rng.normal(0, 0.006, 5000))


@pytest.fixture
def momentum_ds() -> MarketDataset:
    rng = np.random.default_rng(7)
    e = rng.normal(0, 0.006, 5000)
    r = np.zeros_like(e)
    for t in range(1, len(e)):
        r[t] = 0.15 * r[t - 1] + e[t]
    return synthetic_dataset(r)
