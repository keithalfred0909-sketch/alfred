"""BACKTEST ENGINE.

Execution model (no information from the future can reach a decision):

* A signal is evaluated on the close of bar s (all features are causal).
* The order fills on bar f = s + 1 + latency: at its open when real opens exist, otherwise at its close
  (close-only data such as a daily fixing: the next observable price).
* Every fill pays half the spread + commission + slippage (all in bps of price). When the data carries an
  observed per-bar spread, the half spread charged is max(configured, observed) at the fill bar.
* Stops / take-profits are volatility-scaled distances fixed at entry (vol known at s). With high/low data
  they trigger intrabar; if both could trigger in one bar the stop is assumed first (pessimistic); a gap
  through the level fills at the open. With close-only data they are checked on closes only.
* One position at a time. A new signal is accepted from the exit bar onward (filling on the next bar).
* Positions are closed at the end of the evaluation window.

Returns are reported per bar in log units on 1x notional, so different strategies are comparable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from xquant.backtest.metrics import Metrics, compute_metrics
from xquant.config import CostModel


@dataclass
class MarketArrays:
    """Pre-extracted numpy views of the bars used by the hot loop."""

    index: pd.DatetimeIndex
    close: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    vol: np.ndarray  # per-bar sigma of log returns known at each bar (20-bar realised)
    has_ohlc: bool
    ppy: float
    spread_frac: np.ndarray | None = None  # observed bid/ask spread as a fraction of price, per bar

    @staticmethod
    def from_bars(bars: pd.DataFrame, ppy: float) -> MarketArrays:
        lc = np.log(bars["close"])
        vol = lc.diff().rolling(20, min_periods=15).std().to_numpy()
        has = bool(bars[["open", "high", "low"]].notna().all(axis=None))
        spread = None
        if "spread" in bars.columns and bars["spread"].notna().any():
            spread = (bars["spread"] / bars["close"]).to_numpy(float)
        return MarketArrays(pd.DatetimeIndex(bars.index), bars["close"].to_numpy(float), bars["open"].to_numpy(float),
                            bars["high"].to_numpy(float), bars["low"].to_numpy(float), vol, has, ppy, spread)


@dataclass
class BacktestResult:
    returns: pd.Series
    trades: pd.DataFrame
    metrics: Metrics
    in_pos: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0))

    @property
    def trade_net(self) -> np.ndarray:
        return self.trades["net"].to_numpy() if len(self.trades) else np.zeros(0)


TRADE_COLS = ["signal_i", "entry_i", "exit_i", "direction", "entry_px", "exit_px", "gross", "cost", "net", "bars", "reason"]


def run_backtest(m: MarketArrays, entries: np.ndarray, direction: int, hold: int, stop: float | None,
                 take: float | None, costs: CostModel, window: slice, cost_mult: float = 1.0,
                 slippage_mult: float = 1.0, extra_latency: int = 0, entry_shift: int = 0,
                 skip_mask: np.ndarray | None = None) -> BacktestResult:
    a, b = window.start or 0, min(window.stop or len(m.close), len(m.close))
    lat = costs.latency_bars + extra_latency
    fixed_half = costs.spread_bps / 2 * 1e-4
    other = costs.commission_bps * cost_mult * 1e-4 + costs.slippage_bps * slippage_mult * 1e-4
    data_spread = m.spread_frac if (costs.use_data_spread and m.spread_frac is not None) else None

    def fill_cost(i: int) -> float:
        half = fixed_half
        if data_spread is not None and np.isfinite(data_spread[i]):
            half = max(half, data_spread[i] / 2)  # conservative: never cheaper than the configured spread
        return half * cost_mult + other
    lc = np.log(m.close)
    rets = np.zeros(b - a)
    in_pos = np.zeros(b - a, dtype=bool)
    sig_idx = np.flatnonzero(entries[a:b]) + a
    if entry_shift:
        sig_idx = sig_idx + entry_shift
        sig_idx = sig_idx[(sig_idx >= a) & (sig_idx < b)]
    trades: list[tuple] = []
    nxt = a
    k = 0
    while k < len(sig_idx):
        s = int(sig_idx[k])
        k += 1
        if s < nxt:
            continue
        if skip_mask is not None and skip_mask[s]:
            continue
        f = s + 1 + lat
        if f >= b - 1:
            break
        sigma = m.vol[s]
        if not np.isfinite(sigma) or sigma <= 0:
            continue
        entry_px = m.open[f] if m.has_ohlc else m.close[f]
        last = min(f + hold, b - 1)
        dist = sigma * np.sqrt(hold)
        stop_px = entry_px * np.exp(-direction * stop * dist) if stop is not None else None
        take_px = entry_px * np.exp(direction * take * dist) if take is not None else None
        exit_i, exit_px, reason = last, m.close[last], "time"
        start_check = f if m.has_ohlc else f + 1
        for t in range(start_check, last + 1):
            if m.has_ohlc:
                lo, hi, op = m.low[t], m.high[t], m.open[t]
                adverse = lo if direction > 0 else hi
                favour = hi if direction > 0 else lo
                if stop_px is not None and (adverse - stop_px) * direction <= 0:
                    gap = (op - stop_px) * direction <= 0 and t > f
                    exit_i, exit_px, reason = t, (op if gap else stop_px), "stop"
                    break
                if take_px is not None and (favour - take_px) * direction >= 0:
                    gap = (op - take_px) * direction >= 0 and t > f
                    exit_i, exit_px, reason = t, (op if gap else take_px), "take"
                    break
            else:
                c = m.close[t]
                if stop_px is not None and (c - stop_px) * direction <= 0:
                    exit_i, exit_px, reason = t, c, "stop"
                    break
                if take_px is not None and (c - take_px) * direction >= 0:
                    exit_i, exit_px, reason = t, c, "take"
                    break
        # per-bar returns: mark to market from entry price to exit price
        le, lx = np.log(entry_px), np.log(exit_px)
        if exit_i == f:
            rets[f - a] += direction * (lx - le)
        else:
            rets[f - a] += direction * (lc[f] - le)
            if exit_i - 1 > f:
                rets[f + 1 - a:exit_i - a] += direction * np.diff(lc[f:exit_i])
            rets[exit_i - a] += direction * (lx - lc[exit_i - 1])
        c_in, c_out = fill_cost(f), fill_cost(exit_i)
        rets[f - a] -= c_in
        rets[exit_i - a] -= c_out
        in_pos[f - a:exit_i - a + 1] = True
        gross = direction * (lx - le)
        trades.append((s, f, exit_i, direction, entry_px, exit_px, gross, c_in + c_out, gross - c_in - c_out,
                       exit_i - f, reason))
        nxt = exit_i
    tdf = pd.DataFrame(trades, columns=TRADE_COLS)
    if len(tdf):
        tdf["entry_time"] = m.index[tdf["entry_i"].to_numpy()]
        tdf["exit_time"] = m.index[tdf["exit_i"].to_numpy()]
    ser = pd.Series(rets, index=m.index[a:b])
    met = compute_metrics(rets, tdf["net"].to_numpy() if len(tdf) else np.zeros(0), in_pos, m.ppy,
                          tdf["bars"].to_numpy() if len(tdf) else None)
    return BacktestResult(ser, tdf, met, in_pos)
