"""Geometric index built from component price series, e.g. the US Dollar Index (DXY).

    value = constant * prod(close_i ** exponent_i)        on timestamps where EVERY component has a bar

ICE publishes the DXY formula (EUR -0.576, JPY 0.136, GBP -0.119, CAD 0.091, SEK 0.042, CHF 0.036, constant
50.14348112, expressed on EURUSD, USDJPY, GBPUSD, USDCAD, USDSEK, USDCHF). Building it from components gives
an hourly history back to 2005, while the provider's own index series starts much later; the published
series is used to validate the construction, not to replace it.

Bars are combined by exact timestamp (inner join): a timestamp missing in any component is dropped and
counted - never forward-filled - so the index never mixes prices from different moments.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from xquant.data.sources.base import DataSource, build_source, register
from xquant.errors import ConfigError, DataUnavailableError

# ICE US Dollar Index: weights as exponents on the quoted pairs.
DXY_COMPONENTS: list[dict[str, Any]] = [
    {"instrument": "EURUSD", "exponent": -0.576, "point": 1e-5},
    {"instrument": "USDJPY", "exponent": 0.136, "point": 1e-3},
    {"instrument": "GBPUSD", "exponent": -0.119, "point": 1e-5},
    {"instrument": "USDCAD", "exponent": 0.091, "point": 1e-5},
    {"instrument": "USDSEK", "exponent": 0.042, "point": 1e-5},
    {"instrument": "USDCHF", "exponent": 0.036, "point": 1e-5},
]
DXY_CONSTANT = 50.14348112


def combine(closes: dict[str, pd.Series], exponents: dict[str, float], constant: float) -> tuple[pd.Series, int]:
    """Geometric combination on common timestamps. Returns (index series, timestamps dropped)."""
    frame = pd.concat(closes, axis=1, join="outer")
    complete = frame.notna().all(axis=1)
    frame = frame[complete]
    if (frame <= 0).any(axis=None):
        raise ConfigError("basket components must be strictly positive prices")
    log_idx = sum(np.log(frame[k]) * e for k, e in exponents.items()) + np.log(constant)
    return pd.Series(np.exp(log_idx), index=frame.index, name="close"), int((~complete).sum())


@register
class BasketSource(DataSource):
    kind = "basket"

    def __init__(self, components: list[dict[str, Any]] | str, constant: float = 1.0,
                 component_kind: str = "dukascopy_candles", drop: list[str] | None = None,
                 renormalize: bool = False, **common: Any) -> None:
        """``components`` is a list of {instrument, exponent, ...source params} or the preset name "dxy".
        ``drop`` removes components (e.g. ["EURUSD"] for a dollar index ex-EUR); ``renormalize`` rescales the
        remaining exponents so their absolute values sum to 1 (and sets the constant to 1)."""
        if isinstance(components, str) and components != "dxy":
            raise ConfigError(f"unknown basket preset {components!r} (known: 'dxy')")
        comps = [dict(c) for c in (DXY_COMPONENTS if isinstance(components, str) else components)]
        if components == "dxy" and constant == 1.0:
            constant = DXY_CONSTANT
        if drop:
            comps = [c for c in comps if c["instrument"] not in set(drop)]
        if not comps:
            raise ConfigError("basket needs at least one component")
        if renormalize:
            tot = sum(abs(float(c["exponent"])) for c in comps)
            for c in comps:
                c["exponent"] = float(c["exponent"]) / tot
            constant = 1.0
        super().__init__(components=[(c["instrument"], round(float(c["exponent"]), 6)) for c in comps],
                         constant=constant, **common)
        self.comps, self.constant, self.component_kind, self.common = comps, constant, component_kind, common
        self.provenance: dict[str, Any] = {}

    def fetch_series(self) -> pd.DataFrame:
        closes: dict[str, pd.Series] = {}
        exps: dict[str, float] = {}
        for c in self.comps:
            params = {**self.common, **{k: v for k, v in c.items() if k != "exponent"}}
            src = build_source(self.component_kind, params)
            frame = src.fetch_series()
            if frame.empty:
                raise DataUnavailableError(f"basket component {c['instrument']} returned no data")
            closes[c["instrument"]] = frame["close"].astype("float64")
            exps[c["instrument"]] = float(c["exponent"])
            self.provenance[c["instrument"]] = {"bars": int(len(frame)), "exponent": round(exps[c["instrument"]], 6)}
        idx, dropped = combine(closes, exps, self.constant)
        if idx.empty:
            raise DataUnavailableError("basket components share no timestamps")
        self.provenance.update({"bars": int(len(idx)), "timestamps_dropped_incomplete": dropped,
                                "constant": self.constant, "method": "geometric, exact-timestamp inner join"})
        out = idx.to_frame()
        out["value"] = out["close"]
        out.index.name = "timestamp"
        return out
