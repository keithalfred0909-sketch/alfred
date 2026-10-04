"""Event-driven day-trading backtest on 1-minute bars: opening-range breakout (spec nq_orb5_v1).

Bars are stamped at their CLOSE (Dukascopy convention in this lab): the minute 09:30-09:31 New York is the
bar stamped 09:31. The opening candle (09:30-09:35) is therefore bars stamped 09:31..09:35; the entry is
the OPEN of the bar stamped 09:36 (= the 09:35:00 price); the 16:00 exit is the CLOSE of the bar stamped
16:00. Stops/targets are checked minute by minute on high/low; same-minute stop+target -> stop first; a bar
opening beyond the stop fills at its open. Everything a decision uses is printed before the decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

TRADE_COLS = ["date", "side", "entry_time", "entry", "stop", "target", "exit_time", "exit", "reason", "r_gross",
              "cost_r", "r_net", "risk_frac", "stop_dist_frac", "notional_x"]


@dataclass(frozen=True)
class OrbParams:
    open_time: str = "09:30"
    range_minutes: int = 5
    exit_time: str = "16:00"
    min_body_frac: float = 0.10
    target_r: float = 10.0
    min_stop_frac: float = 0.0003
    risk_per_trade: float = 0.01
    max_notional_x: float = 4.0
    cost_per_fill_frac: float = 0.435e-4
    context: str = "none"  # none | weekly_vwap_side
    entry_delay_min: int = 0  # robustness attack: enter N minutes late
    direction_override: Any = None  # robustness attack: dict date -> side (random-direction test)


def _hm(local: pd.DatetimeIndex) -> np.ndarray:
    return np.asarray(local.hour * 60 + local.minute)


def weekly_vwap_minute(bars: pd.DataFrame, local: pd.DatetimeIndex, roll: str = "17:00") -> pd.Series:
    """Tick-volume weighted weekly VWAP (same definition as the feature library), at each minute close."""
    naive = local.tz_localize(None)
    sess_end = (naive - pd.Timedelta(roll + ":00") - pd.Timedelta(seconds=1)).floor("D") + pd.Timedelta(days=1)
    iso = pd.DatetimeIndex(sess_end).isocalendar()
    key = (iso["year"] * 100 + iso["week"]).to_numpy()
    tp = (bars["high"] + bars["low"] + bars["close"]) / 3
    v = bars["volume"].fillna(0.0).clip(lower=0.0)
    cv = v.groupby(key).cumsum().replace(0, np.nan)
    return (tp * v).groupby(key).cumsum() / cv


def run_orb(bars: pd.DataFrame, p: OrbParams, tz: str = "America/New_York") -> pd.DataFrame:
    """One row per trade (and no row for no-trade days). R values are per unit of planned risk."""
    local = pd.DatetimeIndex(bars.index).tz_convert(tz)
    hm = _hm(local)
    day = pd.DatetimeIndex(local.tz_localize(None).normalize())
    o0 = int(p.open_time[:2]) * 60 + int(p.open_time[3:])
    rng_end = o0 + p.range_minutes
    entry_stamp = rng_end + 1 + p.entry_delay_min  # bar whose OPEN is the entry price
    ex = int(p.exit_time[:2]) * 60 + int(p.exit_time[3:])
    o, h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    vwap = weekly_vwap_minute(bars, local).to_numpy() if p.context == "weekly_vwap_side" else None
    rows: list[tuple[Any, ...]] = []
    days, starts = np.unique(day.to_numpy(), return_index=True)
    bounds = list(starts) + [len(bars)]
    for k, d in enumerate(days):
        a, b = bounds[k], bounds[k + 1]
        m = hm[a:b]
        rng_idx = np.flatnonzero((m > o0) & (m <= rng_end)) + a
        ent = np.flatnonzero(m == entry_stamp) + a
        end = np.flatnonzero(m == ex) + a
        if len(rng_idx) != p.range_minutes or not len(ent) or not len(end):
            continue  # no trade: incomplete session data (holiday, half day, gap)
        i_rng0, i_rng1, i_ent, i_end = rng_idx[0], rng_idx[-1], int(ent[0]), int(end[0])
        if i_ent >= i_end:
            continue
        co, cc = o[i_rng0], c[i_rng1]
        ch, cl = h[i_rng0:i_rng1 + 1].max(), lo[i_rng0:i_rng1 + 1].min()
        rng = ch - cl
        if rng <= 0 or abs(cc - co) < p.min_body_frac * rng:
            continue  # doji
        side = 1 if cc > co else -1
        if p.direction_override is not None:
            side = int(p.direction_override.get(pd.Timestamp(d), side))
        if vwap is not None and np.isfinite(vwap[i_rng1]):
            if side * (cc - vwap[i_rng1]) <= 0:
                continue  # context: trade only on the weekly-VWAP side
        entry = o[i_ent]
        stop = cl if side > 0 else ch
        dist = (entry - stop) * side
        if dist <= 0 or dist / entry < p.min_stop_frac:
            continue  # entry already beyond the stop, or stop too tight to execute
        target = entry + side * p.target_r * dist
        exit_px, reason, i_x = c[i_end], "eod", i_end
        for t in range(i_ent, i_end + 1):
            adverse, favour = (lo[t], h[t]) if side > 0 else (h[t], lo[t])
            if (adverse - stop) * side <= 0:
                exit_px = o[t] if (t > i_ent and (o[t] - stop) * side <= 0) else stop
                reason, i_x = "stop", t
                break
            if (favour - target) * side >= 0:
                exit_px = o[t] if (t > i_ent and (o[t] - target) * side >= 0) else target
                reason, i_x = "target", t
                break
        notional = min(p.risk_per_trade / (dist / entry), p.max_notional_x)  # x equity
        risk_frac = notional * dist / entry  # <= risk_per_trade when the notional cap binds
        r_gross = (exit_px - entry) * side / dist
        cost_r = 2 * p.cost_per_fill_frac * entry / dist
        rows.append((pd.Timestamp(d), side, bars.index[i_ent], entry, stop, target, bars.index[i_x], exit_px, reason,
                     r_gross, cost_r, r_gross - cost_r, risk_frac, dist / entry, notional))
    return pd.DataFrame(rows, columns=TRADE_COLS)


def daily_returns(trades: pd.DataFrame) -> pd.Series:
    """Equity return per traded day = R_net x risk actually taken. NOT floored at the daily loss limit: the
    limit stops further trading, it cannot cap the loss of a trade that gaps through its stop."""
    if trades.empty:
        return pd.Series(dtype=float)
    r = trades["r_net"] * trades["risk_frac"]
    return pd.Series(r.to_numpy(), index=pd.DatetimeIndex(trades["date"]))
