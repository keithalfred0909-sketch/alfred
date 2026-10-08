"""Canonical in-memory representation of market data.

Bars: a DataFrame indexed by a tz-aware UTC ``DatetimeIndex`` holding the timestamp at which the bar's
*close* is known (decision time). Columns ``open, high, low, close, volume`` always exist; a column the
source does not provide is all-NaN and the corresponding capability flag is False. Nothing is ever
synthesised to fill a missing column (no fake OHLC from closes, no fake volume).
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from xquant.errors import DataQualityError

BAR_COLUMNS = ["open", "high", "low", "close", "volume"]


@dataclass(frozen=True)
class Capabilities:
    ohlc: bool  # real open/high/low present
    volume: bool
    intraday: bool  # bar size below one day
    ticks: bool = False
    spreads: bool = False

    def describe(self) -> str:
        have = [k for k, v in asdict(self).items() if v]
        return ", ".join(have) if have else "close only"


@dataclass
class DatasetMeta:
    symbol: str
    timeframe: str
    source: str
    sha256: str
    capabilities: Capabilities
    n_rows: int
    start: str
    end: str
    notes: list[str] = field(default_factory=list)
    root_sha256: str = ""  # hash of the ORIGINAL bars this dataset derives from (resampling); "" = itself

    @property
    def root_key(self) -> str:
        """Identity of the underlying prices for the protected-split ledger (M30 built from M1 = same data)."""
        return f"bars:{(self.root_sha256 or self.sha256)[:16]}"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["capabilities"] = asdict(self.capabilities)
        return d


def empty_bars() -> pd.DataFrame:
    idx = pd.DatetimeIndex([], tz="UTC", name="timestamp")
    return pd.DataFrame({c: pd.Series(dtype="float64") for c in BAR_COLUMNS}, index=idx)


def frame_sha256(df: pd.DataFrame) -> str:
    """Content hash of a frame (index + values). Used to version datasets in the experiment tracker."""
    h = hashlib.sha256()
    idx = df.index
    h.update(np.asarray(idx.asi8 if isinstance(idx, pd.DatetimeIndex) else idx).tobytes())  # type: ignore[attr-defined]
    for col in sorted(df.columns):
        h.update(col.encode())
        h.update(np.ascontiguousarray(df[col].to_numpy(dtype="float64", na_value=np.nan)).tobytes())
    return h.hexdigest()


def validate_bars(df: pd.DataFrame) -> None:
    """Hard invariants of the canonical bar frame. Raises DataQualityError when violated."""
    missing = [c for c in BAR_COLUMNS if c not in df.columns]
    if missing:
        raise DataQualityError(f"bars missing columns {missing}")
    if not isinstance(df.index, pd.DatetimeIndex) or df.index.tz is None:
        raise DataQualityError("bars index must be a tz-aware DatetimeIndex")
    if str(df.index.tz) != "UTC":
        raise DataQualityError(f"bars index must be UTC, got {df.index.tz}")
    if not df.index.is_monotonic_increasing or df.index.has_duplicates:
        raise DataQualityError("bars index must be strictly increasing")
    close = df["close"]
    if close.isna().any():
        raise DataQualityError("close may not contain NaN after cleaning")
    if (close <= 0).any():
        raise DataQualityError("non-positive close prices")
    if df[["open", "high", "low"]].notna().all(axis=None):
        bad = (df["high"] < df[["open", "close", "low"]].max(axis=1) - 1e-12) | (
            df["low"] > df[["open", "close", "high"]].min(axis=1) + 1e-12)
        if bad.any():
            raise DataQualityError(f"{int(bad.sum())} bars with inconsistent high/low")


def infer_capabilities(df: pd.DataFrame, timeframe: str) -> Capabilities:
    ohlc = bool(df[["open", "high", "low"]].notna().all(axis=None)) and len(df) > 0
    volume = bool(df["volume"].notna().any()) and bool((df["volume"].fillna(0) > 0).any())
    intraday = bar_timedelta(timeframe) < pd.Timedelta("1D")
    return Capabilities(ohlc=ohlc, volume=volume, intraday=intraday)


def bar_timedelta(timeframe: str) -> pd.Timedelta:
    """Nominal bar size from a timeframe string such as '1D', '4h', '5min'."""
    try:
        return pd.Timedelta(timeframe)
    except ValueError:
        return pd.Timedelta(1, unit="D") if timeframe.upper() in {"D", "1D", "DAILY"} else pd.Timedelta(timeframe.lower())
