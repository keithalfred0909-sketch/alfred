"""Position-sizing / portfolio rules. Every rule returns TARGET WEIGHTS decided at the close of day t using
data up to and including t; the engine applies them to the return of day t+1 (never the same day)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rebalance_days(index: pd.DatetimeIndex, freq: str, tz: str = "America/New_York") -> np.ndarray:
    """Last session of each calendar month ('M') or ISO week ('W') in local time."""
    local = index.tz_convert(tz) if index.tz is not None else index
    iso = local.isocalendar()
    k = np.asarray(local.year * 100 + local.month) if freq == "M" else np.asarray(iso["year"] * 100 + iso["week"])
    return np.r_[k[1:] != k[:-1], True]


def hold_between(target: pd.DataFrame, rebalance: np.ndarray) -> pd.DataFrame:
    """Weights set on rebalance days and held (forward-filled) until the next one. On a rebalance day an
    instrument without a signal gets weight 0 (it is not carried over from the previous rebalance)."""
    t = target.fillna(0.0)
    t.loc[~rebalance] = np.nan
    return t.ffill().fillna(0.0)


def fit_scale(raw: pd.Series, train: pd.Series, cap: float, target: float = 1.0) -> float:
    """c such that mean(min(c * raw, cap)) over TRAIN equals ``target`` (bisection; raw > 0)."""
    x = raw[train].dropna().to_numpy()
    if not len(x) or np.minimum(x * 1e9, cap).mean() < target:
        raise ValueError("cannot reach the target average exposure under the cap")
    lo, hi = 0.0, 1.0
    while np.minimum(hi * x, cap).mean() < target:
        hi *= 2
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if np.minimum(mid * x, cap).mean() < target else (lo, mid)
    return (lo + hi) / 2


def vol_managed(daily_ret: pd.Series, hourly_ret: pd.Series | None, rv: str, window: int, cap: float,
                train: pd.Series) -> tuple[pd.Series, dict[str, float]]:
    """w_t = min(c / RV_t, cap); RV from the last ``window`` daily returns or from hourly returns over the last
    ``window`` sessions, annualised. c is fitted on TRAIN so the average TRAIN weight is 1."""
    if rv == "daily":
        var = (daily_ret ** 2).rolling(window, min_periods=window).mean() * 252
    elif rv == "hourly":
        if hourly_ret is None:
            raise ValueError("hourly returns required")
        sess = hourly_ret.groupby(daily_ret.index.searchsorted(hourly_ret.index, side="left")).apply(
            lambda s: float((s ** 2).sum()))
        valid = sess[sess.index < len(daily_ret)]
        per_session = pd.Series(valid.to_numpy(), index=daily_ret.index[valid.index.to_numpy()]).reindex(daily_ret.index)
        var = per_session.rolling(window, min_periods=window).sum() * 252 / window
    else:
        raise ValueError(f"unknown rv {rv}")
    raw = 1.0 / var.replace(0, np.nan)
    c = fit_scale(raw, train, cap)
    w = (c * raw).clip(upper=cap)
    return w.rename("w"), {"scale_c": c, "train_mean_weight": float(w[train].mean())}


def tsmom(closes: pd.DataFrame, lookback: int, vol_window: int = 60, target_vol: float = 0.10,
          max_pos: float = 3.0) -> pd.DataFrame:
    lc = closes.transform(np.log)
    sig = np.sign(lc - lc.shift(lookback))
    vol = lc.diff().rolling(vol_window, min_periods=vol_window).std() * np.sqrt(252)
    pos = sig * np.minimum(target_vol / vol, max_pos)
    n = pos.notna().sum(axis=1).replace(0, np.nan)
    target = pos.div(n, axis=0)
    return hold_between(target, _rebalance_days(pd.DatetimeIndex(closes.index), "M"))


def xs_momentum(closes: pd.DataFrame, lookback: int, n_side: int = 2, leg: float = 0.5) -> pd.DataFrame:
    lc = closes.transform(np.log)
    past = lc - lc.shift(lookback)
    rank = past.rank(axis=1, method="first")
    k = past.notna().sum(axis=1)
    long_ = rank.gt(k - n_side, axis=0) & past.notna()
    short = rank.le(n_side, axis=0) & past.notna()
    target = long_.astype(float) * leg - short.astype(float) * leg
    target.loc[k < 2 * n_side] = 0.0
    return hold_between(target, _rebalance_days(pd.DatetimeIndex(closes.index), "W"))
