"""Performance metrics from per-bar strategy returns and the trade list."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass
class Metrics:
    total_return: float = 0.0
    cagr: float = 0.0
    ann_vol: float = 0.0
    sharpe: float = 0.0
    sortino: float = 0.0
    max_drawdown: float = 0.0
    calmar: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0  # mean net return per trade (log units)
    win_rate: float = 0.0
    trades: int = 0
    exposure: float = 0.0
    avg_bars: float = 0.0
    stability: float = 0.0  # R^2 of cumulative log equity vs time
    years: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {k: (None if isinstance(v, float) and not math.isfinite(v) else v)  # type: ignore[misc]
                for k, v in asdict(self).items()}


def compute_metrics(rets: np.ndarray, trade_net: np.ndarray, in_pos: np.ndarray, ppy: float,
                    trade_bars: np.ndarray | None = None) -> Metrics:
    r = np.nan_to_num(np.asarray(rets, dtype=float))
    m = Metrics()
    n = len(r)
    if n == 0:
        return m
    m.years = n / ppy
    eq = np.cumsum(r)  # log equity, unit notional
    m.total_return = float(math.expm1(eq[-1]))
    m.cagr = float(math.expm1(eq[-1] / m.years)) if m.years > 0 else 0.0
    sd = r.std(ddof=1) if n > 1 else 0.0
    m.ann_vol = float(sd * math.sqrt(ppy))
    m.sharpe = float(r.mean() / sd * math.sqrt(ppy)) if sd > 0 else 0.0
    downside = np.sqrt(np.mean(np.minimum(r, 0.0) ** 2))
    m.sortino = float(r.mean() / downside * math.sqrt(ppy)) if downside > 0 else 0.0
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    dd = 1 - np.exp(eq - peak)
    m.max_drawdown = float(dd.max()) if len(dd) else 0.0
    m.calmar = m.cagr / m.max_drawdown if m.max_drawdown > 0 else 0.0
    t = np.asarray(trade_net, dtype=float)
    m.trades = int(len(t))
    if len(t):
        gains, losses = t[t > 0].sum(), -t[t < 0].sum()
        m.profit_factor = float(gains / losses) if losses > 0 else (float("inf") if gains > 0 else 0.0)
        m.expectancy = float(t.mean())
        m.win_rate = float((t > 0).mean())
    m.exposure = float(np.mean(in_pos)) if len(in_pos) else 0.0
    if trade_bars is not None and len(trade_bars):
        m.avg_bars = float(np.mean(trade_bars))
    if n > 10 and np.ptp(eq) > 0:
        x = np.arange(n)
        m.stability = float(np.corrcoef(x, eq)[0, 1] ** 2) * (1 if eq[-1] > 0 else -1)
    return m


def yearly_returns(rets: pd.Series) -> pd.Series:
    return rets.groupby(pd.DatetimeIndex(rets.index).year).sum()
