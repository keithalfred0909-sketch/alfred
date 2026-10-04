"""MetaTrader 5 history export (Symbols -> Bars -> Export, or a script using CopyRates).

Expected file: tab- or comma-separated with the MT5 header
``<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>`` (``<TIME>`` absent for daily bars),
dates like ``2024.01.02``. Timestamps are bar OPEN times in the broker's SERVER time, which is rarely UTC:

    server_tz: "nyclose"      UTC+2 in winter / UTC+3 in summer following US DST (the usual FX convention)
    server_tz: "+02:00"       fixed offset
    server_tz: "Europe/Athens" any IANA zone

Getting this wrong shifts every bar by hours and silently breaks time-of-day research, so the engine
cross-check against an independent reference (if configured) is strongly recommended.
``<SPREAD>`` is the broker-reported bar spread in points (MT5 semantics vary by broker; treated as indicative).
``<TICKVOL>`` is tick count, not exchange volume.
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

from xquant.data.schema import bar_timedelta
from xquant.data.sources.base import DataSource, register
from xquant.errors import ConfigError, DataQualityError, DataUnavailableError


def server_to_utc(naive: pd.DatetimeIndex, server_tz: str) -> pd.DatetimeIndex:
    if server_tz.lower() == "nyclose":
        ny = (naive - pd.Timedelta(hours=7)).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT")
        return ny.tz_convert("UTC")
    m = re.fullmatch(r"([+-])(\d{2}):(\d{2})", server_tz)
    if m:
        sign = 1 if m.group(1) == "+" else -1
        off = pd.Timedelta(hours=int(m.group(2)), minutes=int(m.group(3)))
        return (naive - sign * off).tz_localize("UTC")
    try:
        return naive.tz_localize(server_tz, ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
    except Exception as exc:
        raise ConfigError(f"unknown server_tz {server_tz!r}") from exc


@register
class Mt5CsvSource(DataSource):
    kind = "mt5_csv"

    def __init__(self, path: str, server_tz: str, bar: str, point: float, **extra: Any) -> None:
        super().__init__(path=path, server_tz=server_tz, bar=bar, point=point)
        self.path = self.resolve_path(path)
        self.server_tz, self.bar, self.point = server_tz, bar, point
        self.provenance: dict[str, Any] = {}

    def fetch_series(self) -> pd.DataFrame:
        if not self.path.exists():
            raise DataUnavailableError(f"MT5 export not found: {self.path}")
        df = pd.read_csv(self.path, sep=None, engine="python")
        df.columns = [str(c).strip().strip("<>").upper() for c in df.columns]
        need = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not need <= set(df.columns):
            raise DataQualityError(f"{self.path.name}: expected MT5 columns {sorted(need)}, got {list(df.columns)}")
        stamp = df["DATE"].astype(str) + (" " + df["TIME"].astype(str) if "TIME" in df.columns else "")
        naive = pd.DatetimeIndex(pd.to_datetime(stamp, format="mixed", errors="coerce"))
        utc = server_to_utc(naive, self.server_tz) + bar_timedelta(self.bar)  # stamp at bar close
        out = pd.DataFrame({c.lower(): pd.to_numeric(df[c], errors="coerce").to_numpy()
                            for c in ["OPEN", "HIGH", "LOW", "CLOSE"]}, index=pd.DatetimeIndex(utc, name="timestamp"))
        out["volume"] = pd.to_numeric(df["TICKVOL"], errors="coerce").to_numpy() if "TICKVOL" in df.columns else np.nan
        if "SPREAD" in df.columns:
            out["spread"] = pd.to_numeric(df["SPREAD"], errors="coerce").to_numpy() * self.point
        nat = np.asarray(out.index.isna())
        dropped = int(nat.sum())
        out = out[~nat]
        self.provenance = {"file": self.path.name, "rows": int(len(df)), "server_tz": self.server_tz,
                           "dst_ambiguous_dropped": dropped, "volume": "MT5 tick volume (not exchange volume)"}
        return out
