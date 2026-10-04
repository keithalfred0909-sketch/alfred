"""Coarser bars built from another asset's (already validated) bars.

Used for EUR/USD daily OHLC: hourly Dukascopy bars -> daily sessions closing at 17:00 New York (the FX
convention), so the daily dataset inherits the hourly source's validation (format checks + Fed cross-check)
without any extra download or a second, unverified daily-candle convention.

A session D contains every bar that closes in (D-1 17:00, D 17:00] local time and is stamped at D 17:00.
Sessions with fewer than ``min_bars`` bars (holidays, partial weeks) are dropped and counted - never padded.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from xquant.data.sources.base import DataSource, register
from xquant.errors import DataQualityError


def aggregate_sessions(bars: pd.DataFrame, session_close: str = "17:00", tz: str = "America/New_York",
                       min_bars: int = 12) -> tuple[pd.DataFrame, dict[str, Any]]:
    # Work in naive local wall-clock time: "+1 day" must mean one calendar day, also across DST changes.
    local = pd.DatetimeIndex(bars.index).tz_convert(tz).tz_localize(None)
    close_td = pd.Timedelta(session_close + ":00")
    day = (local - close_td - pd.Timedelta(seconds=1)).floor("D") + pd.Timedelta(days=1)
    key = pd.Series(day, index=bars.index)
    g = bars.groupby(key.to_numpy())
    agg: dict[str, Any] = {"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                           "close": g["close"].last(), "volume": g["volume"].sum(min_count=1),
                           "n": g["close"].size()}
    if "spread" in bars.columns:
        agg["spread"] = g["spread"].mean()
    out = pd.DataFrame(agg)
    short = out["n"] < min_bars
    stamps = (pd.DatetimeIndex(out.index) + close_td).tz_localize(tz, ambiguous="NaT", nonexistent="shift_forward")
    out.index = stamps.tz_convert("UTC").rename("timestamp")
    info = {"sessions": int(len(out)), "short_sessions_dropped": int(short.sum()), "session_close": f"{session_close} {tz}",
            "median_bars_per_session": float(out["n"].median()) if len(out) else 0.0}
    out = out[~short.to_numpy()].drop(columns="n")
    out = out[out.index.notna()]
    return out, info


@register
class ResampledAssetSource(DataSource):
    kind = "resample_asset"

    def __init__(self, asset: str, session_close: str = "17:00", tz: str = "America/New_York", min_bars: int = 12,
                 offline: bool = False, **extra: Any) -> None:
        super().__init__(asset=asset, session_close=session_close, tz=tz)
        self.asset, self.session_close, self.tz, self.min_bars = asset, session_close, tz, min_bars
        self.offline = offline
        self.provenance: dict[str, Any] = {}

    def fetch_series(self) -> pd.DataFrame:
        from xquant.config import load_config
        from xquant.data.engine import DataEngine
        base_cfg = load_config(self.asset)
        bars, meta, rep = DataEngine(base_cfg.asset, offline=self.offline).load_bars()
        if not meta.capabilities.ohlc:
            raise DataQualityError(f"{self.asset} has no OHLC; cannot build session bars")
        out, info = aggregate_sessions(bars, self.session_close, self.tz, self.min_bars)
        self.provenance = {"from": f"{self.asset} ({meta.source})", "base_sha256": meta.sha256,
                           "base_notes": meta.notes, **info}
        return out
