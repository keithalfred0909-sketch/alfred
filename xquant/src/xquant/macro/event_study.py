"""Event studies: what does the market actually do around a class of events?

For an event at time e, the *reaction* is the log return from the last bar strictly before e to the first
bar at or after e; *drift* is the return over the following h bars. Questions asked per event class:

1. volatility: is |reaction| larger than |return| on comparable non-event bars?
2. direction: does the standardised surprise predict the reaction sign (HAC slope)?
3. drift: does the reaction continue or revert over the next h bars?
4. interaction: does the surprise->reaction relation differ by market regime?

No direction is assumed (e.g. "hot CPI = USD up"); the sign comes out of the data or not at all.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from xquant.findings import Finding
from xquant.stats import TestResult, hac_conditional_diff, hac_mean_test


def map_events_to_bars(event_times: pd.DatetimeIndex, bar_index: pd.DatetimeIndex) -> np.ndarray:
    """Position of the first bar at/after each event (or -1 when beyond the data)."""
    pos = bar_index.searchsorted(event_times, side="left")
    return np.where(pos < len(bar_index), pos, -1)


def slope_test(x: np.ndarray, y: np.ndarray) -> TestResult:
    """OLS slope of y on x with HC standard errors (events are sparse: no serial overlap)."""
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 15 or np.std(x) == 0:
        return TestResult(float("nan"), float("nan"), float("nan"), n)
    X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    cov = XtX_inv @ (X.T * u**2) @ X @ XtX_inv
    t = b[1] / np.sqrt(cov[1, 1])
    from scipy import stats as sps
    return TestResult(float(t), float(2 * sps.t.sf(abs(t), n - 2)), float(b[1]), n)


def event_study(events: pd.DataFrame, close: pd.Series, mask: np.ndarray, label: str, engine: str,
                period: str, drift_h: int = 5, regimes: pd.Series | None = None,
                min_events: int = 30) -> list[Finding]:
    """``events``: UTC-indexed frame with ``std_surprise`` (may be NaN). ``mask`` restricts to a split."""
    lc = np.log(close)
    idx = pd.DatetimeIndex(close.index)
    pos = map_events_to_bars(pd.DatetimeIndex(events.index), idx)
    keep = (pos > 0) & np.array([mask[p] if p >= 0 else False for p in pos])
    ev, pos = events[keep], pos[keep]
    out: list[Finding] = []
    if len(ev) < min_events:
        return [Finding.insufficient(engine, "event_study", f"{label}",
                                     f"{len(ev)} events in sample (< {min_events})")]
    lcv = lc.to_numpy()
    reaction = lcv[pos] - lcv[pos - 1]
    drift = np.array([lcv[min(p + drift_h, len(lcv) - 1)] - lcv[p] if p + drift_h < len(lcv) else np.nan for p in pos])

    # 1) volatility on event bars vs all other bars in the split
    r = lc.diff().abs().to_numpy()
    is_event = np.zeros(len(r), dtype=bool)
    is_event[pos] = True
    res = hac_conditional_diff(r[mask], is_event[mask], lags=1)
    out.append(Finding.from_test(engine, "event_volatility", f"{label}_abs_reaction",
                                 f"|bar return| on {label} bars vs non-event bars", res, period))
    # 2) direction: surprise -> reaction
    if "std_surprise" in ev and ev["std_surprise"].notna().sum() >= min_events:
        s = ev["std_surprise"].to_numpy(dtype=float)
        out.append(Finding.from_test(engine, "event_direction", f"{label}_surprise_to_reaction",
                                     f"slope of reaction on standardised surprise ({label})",
                                     slope_test(s, reaction), period))
        out.append(Finding.from_test(engine, "event_drift", f"{label}_surprise_to_drift",
                                     f"slope of next-{drift_h}-bar drift on standardised surprise ({label})",
                                     slope_test(s, drift), period))
        if regimes is not None:
            rg = regimes.to_numpy()[pos]
            for k in sorted(set(rg[np.isfinite(rg)].astype(int))):
                sel = rg == k
                if sel.sum() >= min_events:
                    out.append(Finding.from_test(engine, "event_regime", f"{label}_surprise_reaction_regime{k}",
                                                 f"surprise->reaction slope within regime {k} ({label})",
                                                 slope_test(s[sel], reaction[sel]), period))
    else:
        out.append(Finding.insufficient(engine, "event_direction", f"{label}_surprise_to_reaction",
                                        "no consensus/standardised surprise available: cannot separate surprise from release"))
    # 3) drift continuation after the reaction
    out.append(Finding.from_test(engine, "event_drift", f"{label}_reaction_continuation",
                                 f"sign(reaction) x next-{drift_h}-bar return ({label}); >0 continuation",
                                 hac_mean_test(np.sign(reaction) * drift, lags=0), period))
    return out


def summarize_reactions(events: pd.DataFrame, close: pd.Series) -> dict[str, Any]:
    lc = np.log(close).to_numpy()
    pos = map_events_to_bars(pd.DatetimeIndex(events.index), pd.DatetimeIndex(close.index))
    pos = pos[pos > 0]
    rx = lc[pos] - lc[pos - 1]
    return {"events": int(len(pos)), "mean_abs_reaction_bps": float(np.mean(np.abs(rx)) * 1e4) if len(rx) else None}
