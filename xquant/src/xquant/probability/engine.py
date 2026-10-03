"""PROBABILITY ENGINE: historical scenario frequencies under the *current* conditions.

Given the latest bar, find past bars in the same state (same tail bucket for each conditioning feature,
optionally same regime) and tabulate what happened over the next H bars:

    A: up    (return >  +k * typical H-bar move)
    B: flat
    C: down  (return <  -k * typical H-bar move)

Reported with sample size, period, Wilson 95% intervals, the unconditional baseline and a chi-square
test of conditional vs baseline frequencies. These are historical frequencies, not forecasts: if the
test is not significant, the report says the conditions add no information over the baseline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as sps

from xquant.stats import forward_returns, wilson_interval


@dataclass
class ScenarioReport:
    asset: str
    as_of: str
    horizon: int
    conditions: list[str]
    sample_size: int
    period: str
    scenarios: dict[str, dict[str, Any]]
    baseline: dict[str, float]
    p_value_vs_baseline: float
    informative: bool
    invalidation: list[str]
    notes: list[str] = field(default_factory=list)
    status: str = "OK"

    def to_dict(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        if not math.isfinite(d["p_value_vs_baseline"]):
            d["p_value_vs_baseline"] = None
        return d


def _bucket(x: pd.Series, ref: pd.Series) -> pd.Series:
    """Quintile bucket using thresholds from ``ref`` (the history excluding the forecast window)."""
    edges = ref.dropna().quantile([0.2, 0.4, 0.6, 0.8]).to_numpy()
    return pd.Series(np.searchsorted(edges, x.to_numpy(), side="right"), index=x.index).where(x.notna())


def scenario_analysis(asset: str, close: pd.Series, features: dict[str, pd.Series], horizon: int,
                      regimes: pd.Series | None = None, k: float = 0.5, min_sample: int = 30,
                      max_conditions: int = 3) -> ScenarioReport:
    lc = np.log(close)
    fwd = forward_returns(lc, horizon)
    hist = fwd.notna()  # bars whose outcome is known
    typical = float(fwd[hist].abs().median())
    thr = k * typical
    labels = pd.Series(np.select([fwd > thr, fwd < -thr], ["A_up", "C_down"], "B_flat"), index=fwd.index)[hist]
    last = close.index[-1]
    cond_mask = pd.Series(True, index=close.index)
    conditions: list[str] = []
    invalidation: list[str] = []
    for name, x in list(features.items())[:max_conditions]:
        b = _bucket(x, x[hist])
        cur = b.iloc[-1]
        if not np.isfinite(cur):
            continue
        trial = cond_mask & (b == cur)
        if int((trial & hist).sum()) < min_sample:
            break
        cond_mask = trial
        conditions.append(f"{name} in quintile {int(cur) + 1}/5 (current value {x.iloc[-1]:.4g})")
        invalidation.append(f"{name} leaves quintile {int(cur) + 1}")
    if regimes is not None and np.isfinite(regimes.iloc[-1]):
        trial = cond_mask & (regimes == regimes.iloc[-1])
        if int((trial & hist).sum()) >= min_sample:
            cond_mask = trial
            conditions.append(f"regime == {int(regimes.iloc[-1])}")
            invalidation.append("regime changes")
    sel = labels[cond_mask[hist]]
    n = len(sel)
    names = ["A_up", "B_flat", "C_down"]
    base_counts = labels.value_counts().reindex(names, fill_value=0)
    base: dict[str, float] = {str(k_): float(v) for k_, v in (base_counts / base_counts.sum()).items()}
    if n < min_sample:
        return ScenarioReport(asset, str(last), horizon, conditions, n, "", {}, base, float("nan"), False,
                              invalidation, status="INSUFFICIENT DATA")
    counts = sel.value_counts().reindex(names, fill_value=0)
    scen = {}
    for s in names:
        lo, hi = wilson_interval(int(counts[s]), n)
        scen[s] = {"probability": float(counts[s] / n), "ci95": [lo, hi], "count": int(counts[s]),
                   "definition": {"A_up": f"> +{thr:.4%}", "B_flat": f"within +/-{thr:.4%}", "C_down": f"< -{thr:.4%}"}[s]}
    expected = np.array([base[s] for s in names]) * n
    chi = float(((counts.to_numpy() - expected) ** 2 / np.maximum(expected, 1e-9)).sum())
    # Overlapping H-bar windows: deflate the statistic by H (effective sample ~ n / H).
    p = float(sps.chi2.sf(chi / max(horizon, 1), 2))
    idx = sel.index
    rep = ScenarioReport(asset, str(last), horizon, conditions, n, f"{idx[0].date()} to {idx[-1].date()}", scen,
                         dict(base), p, bool(p < 0.05), invalidation)
    if not rep.informative:
        rep.notes.append("Conditional frequencies are not significantly different from the unconditional baseline: "
                         "the current conditions carry no demonstrated information about the next move.")
    rep.notes.append("Historical frequencies over overlapping windows; not a forecast and not investment advice.")
    return rep
