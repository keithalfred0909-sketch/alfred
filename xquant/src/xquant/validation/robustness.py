"""WALK-FORWARD, MONTE CARLO and ROBUSTNESS engines.

All functions take an ``EvalContext`` and a genome; none of them touch TEST or FINAL - they operate on
the windows the caller passes (TRAIN and VALIDATION during selection).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import replace
from typing import Any

import numpy as np
import pandas as pd

from xquant.backtest.engine import BacktestResult, run_backtest
from xquant.config import CostModel
from xquant.stats import sharpe, stationary_bootstrap_indices
from xquant.strategy.evaluator import EvalContext
from xquant.strategy.genome import Genome, neighbours

# --------------------------------------------------------------------------------------- walk-forward


def walk_forward(ctx: EvalContext, g: Genome, region: slice, n_windows: int, mode: str = "rolling",
                 reoptimize_hold: bool = True) -> dict[str, Any]:
    """Re-fit thresholds (and optionally pick the holding period among neighbours) on each in-sample
    window, trade the following out-of-sample window. Returns stitched OOS statistics."""
    a, b = region.start or 0, region.stop
    total = b - a
    oos_len = total // (n_windows + 2)
    is_len = 2 * oos_len
    if oos_len < 60:
        return {"status": "INSUFFICIENT DATA", "reason": f"OOS window of {oos_len} bars"}
    oos_rets, is_srs, oos_srs, windows = [], [], [], []
    for w in range(n_windows):
        oos_start = a + is_len + w * oos_len
        oos_end = min(oos_start + oos_len, b)
        is_start = a if mode == "expanding" else oos_start - is_len
        fit = slice(is_start, oos_start)
        cand = [g]
        if reoptimize_hold:
            cand += [replace(g, hold=h) for h in {max(1, g.hold // 2), g.hold * 2} if h != g.hold]
        scored = [(ctx.backtest(c, fit, fit), c) for c in cand]
        is_res, chosen = max(scored, key=lambda x: x[0].metrics.sharpe)
        oos = ctx.backtest(chosen, fit, slice(oos_start, oos_end))
        oos_rets.append(oos.returns)
        is_srs.append(is_res.metrics.sharpe)
        oos_srs.append(oos.metrics.sharpe)
        windows.append({"oos": [str(ctx.market.index[oos_start].date()), str(ctx.market.index[oos_end - 1].date())],
                        "hold": chosen.hold, "is_sharpe": is_res.metrics.sharpe, "oos_sharpe": oos.metrics.sharpe,
                        "oos_trades": oos.metrics.trades})
    stitched = pd.concat(oos_rets)
    is_mean = float(np.mean(is_srs))
    return {"status": "OK", "mode": mode, "windows": windows,
            "oos_sharpe": sharpe(stitched.to_numpy(), ctx.market.ppy),
            "oos_total": float(np.expm1(stitched.sum())),
            "positive_windows": float(np.mean([s > 0 for s in oos_srs])),
            "efficiency": float(np.mean(oos_srs) / is_mean) if is_mean > 0 else float("nan"),
            "returns": stitched}


# ---------------------------------------------------------------------------------------- Monte Carlo


def trade_bootstrap(trade_net: np.ndarray, reps: int, rng: np.random.Generator) -> dict[str, Any]:
    t = np.asarray(trade_net, dtype=float)
    if len(t) < 10:
        return {"status": "INSUFFICIENT DATA", "trades": int(len(t))}
    sims = rng.choice(t, size=(reps, len(t)), replace=True)
    eq = np.cumsum(sims, axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.zeros((reps, 1)), eq], axis=1), axis=1)[:, 1:]
    mdd = (1 - np.exp(eq - peak)).max(axis=1)
    tot = np.expm1(eq[:, -1])
    return {"status": "OK", "p_loss": float((tot <= 0).mean()), "total_p05": float(np.quantile(tot, 0.05)),
            "total_p50": float(np.median(tot)), "max_dd_p95": float(np.quantile(mdd, 0.95))}


def bootstrap_sharpe_ci(rets: np.ndarray, ppy: float, reps: int, rng: np.random.Generator,
                        block: float = 20.0) -> dict[str, float]:
    r = np.asarray(rets, dtype=float)
    if len(r) < 100:
        return {"lo": float("nan"), "hi": float("nan")}
    vals = [sharpe(r[stationary_bootstrap_indices(len(r), block, rng)], ppy) for _ in range(reps)]
    return {"lo": float(np.quantile(vals, 0.025)), "hi": float(np.quantile(vals, 0.975)),
            "p_le_0": float(np.mean(np.array(vals) <= 0))}


def random_entry_test(ctx: EvalContext, g: Genome, actual: BacktestResult, window: slice, reps: int,
                      rng: np.random.Generator) -> dict[str, Any]:
    """Null distribution: same number of entries at random bars, same direction/exit logic and costs."""
    n_tr = actual.metrics.trades
    a, b = window.start or 0, window.stop
    if n_tr < 5:
        return {"status": "INSUFFICIENT DATA"}
    act = float(actual.returns.sum())
    valid = np.flatnonzero(np.isfinite(ctx.market.vol[a:b - g.hold - 2])) + a
    null = np.empty(reps)
    gap = g.hold + 2 + ctx.costs.latency_bars
    for i in range(reps):
        sig = np.zeros(len(ctx.market.close), dtype=bool)
        busy = np.zeros(len(ctx.market.close) + gap + 1, dtype=bool)
        taken = 0
        for p in rng.permutation(valid):  # non-overlapping random entries: each one becomes a trade
            if not busy[p]:
                sig[p] = True
                busy[max(0, p - gap):p + gap + 1] = True
                taken += 1
                if taken >= n_tr:
                    break
        null[i] = run_backtest(ctx.market, sig, g.direction, g.hold, g.stop, g.take, ctx.costs, window,
                               trail=g.trail).returns.sum()
    return {"status": "OK", "p_value": float((1 + (null >= act).sum()) / (1 + reps)), "actual": act,
            "null_mean": float(null.mean()), "null_p95": float(np.quantile(null, 0.95))}


def randomized_execution(ctx: EvalContext, g: Genome, fit: slice, window: slice, reps: int,
                         rng: np.random.Generator, skip_frac: float = 0.1) -> dict[str, Any]:
    fs = ctx.fit(g, fit)
    sig = ctx.signal(fs)
    srs = []
    for _ in range(reps):
        skip = rng.random(len(sig)) < skip_frac
        res = run_backtest(ctx.market, sig, g.direction, g.hold, g.stop, g.take, ctx.costs, window, trail=g.trail,
                           extra_latency=int(rng.integers(0, 2)), skip_mask=skip)
        srs.append(res.metrics.sharpe)
    return {"median_sharpe": float(np.median(srs)), "positive_share": float(np.mean(np.array(srs) > 0))}


# ----------------------------------------------------------------------------------------- robustness


def parameter_perturbation(ctx: EvalContext, g: Genome, fit: slice, window: slice, scale: float) -> dict[str, Any]:
    nb = neighbours(g, scale)
    res = [ctx.backtest(n, fit, window).metrics for n in nb]
    if not res:
        return {"status": "INSUFFICIENT DATA"}
    prof = [m.sharpe > 0 and m.total_return > 0 for m in res]
    return {"status": "OK", "neighbours": len(nb), "profitable_share": float(np.mean(prof)),
            "median_sharpe": float(np.median([m.sharpe for m in res])),
            "worst_sharpe": float(min(m.sharpe for m in res))}


def cost_stress(ctx: EvalContext, g: Genome, fit: slice, window: slice, multipliers: list[float]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    fs = ctx.fit(g, fit)
    for mlt in multipliers:
        r = ctx.backtest(g, fit, window, fitted=fs, cost_mult=mlt, slippage_mult=mlt, count=False).metrics
        out[f"x{mlt:g}"] = {"sharpe": r.sharpe, "total_return": r.total_return, "pf": r.profit_factor}
    lat = ctx.backtest(g, fit, window, fitted=fs, extra_latency=1, count=False).metrics
    out["latency_plus1"] = {"sharpe": lat.sharpe, "total_return": lat.total_return}
    # Only DELAYED entries: shifting earlier would act before the signal exists (look-ahead by construction).
    for sh in (1, 2):
        r = ctx.backtest(g, fit, window, fitted=fs, entry_shift=sh, count=False).metrics
        out[f"entry_shift_{sh:+d}"] = {"sharpe": r.sharpe, "total_return": r.total_return}
    return out


def data_perturbation(rebuild: Callable[[pd.DataFrame], EvalContext], bars: pd.DataFrame, g: Genome,
                      fit: slice, window: slice, frac: float, reps: int, rng: np.random.Generator) -> dict[str, Any]:
    """Add i.i.d. noise of ``frac`` x local volatility to log prices, rebuild every feature, re-run."""
    lc = np.log(bars["close"])
    vol = lc.diff().rolling(20, min_periods=15).std().bfill().to_numpy()
    srs = []
    for _ in range(reps):
        noisy = bars.copy()
        noisy["close"] = np.exp(lc.to_numpy() + rng.normal(0, 1, len(lc)) * frac * vol)
        c2 = rebuild(noisy)
        srs.append(c2.backtest(g, fit, window, count=False).metrics.sharpe)
    return {"median_sharpe": float(np.median(srs)), "positive_share": float(np.mean(np.array(srs) > 0)), "reps": reps}


def timeframe_perturbation(rebuild: Callable[[pd.DataFrame], EvalContext], bars: pd.DataFrame, g: Genome,
                           fit: slice, window: slice, min_trades: int) -> dict[str, Any]:
    """Resample to every 2nd bar (both phases). Feature windows keep their length in bars, so the test asks
    whether the effect survives a coarser sampling, not whether parameters transfer exactly."""
    out = {}
    for phase in (0, 1):
        sub = bars.iloc[phase::2]
        c2 = rebuild(sub)
        f2 = slice((fit.start or 0) // 2, fit.stop // 2)
        w2 = slice((window.start or 0) // 2, window.stop // 2)
        missing = [c.feature for c in g.conditions if not c2.exprs[c.feature].primitives() <= set(c2.prims)]
        if missing:  # e.g. sub-hourly session features do not exist on the coarser bars
            out[f"phase{phase}"] = {"sharpe": float("nan"), "trades": 0, "status": f"NOT APPLICABLE (no {missing})"}
            continue
        res = c2.backtest(replace(g, hold=max(1, g.hold // 2)), f2, w2, count=False).metrics
        out[f"phase{phase}"] = {"sharpe": res.sharpe, "trades": res.trades,
                                "status": "OK" if res.trades >= min_trades // 2 else "INSUFFICIENT DATA"}
    return out


def breakdowns(res: BacktestResult, regimes: pd.Series | None, tz: str) -> dict[str, Any]:
    r = res.returns
    years = r.groupby(pd.DatetimeIndex(r.index).year).sum()
    out: dict[str, Any] = {"yearly": {int(k): float(v) for k, v in years.items()},  # type: ignore[call-overload]
                           "profitable_year_share": float((years > 0).mean()) if len(years) else 0.0}
    t = res.trades
    if len(t):
        net = t["net"].to_numpy()
        total = net.sum()
        k = max(1, int(math.ceil(0.05 * len(net))))
        top = np.sort(net)[::-1][:k].sum()
        out["top5pct_trade_share"] = float(top / total) if total > 0 else float("inf")
        months = r.groupby(pd.DatetimeIndex(r.index).tz_localize(None).to_period("M")).sum()
        out["without_best_month"] = float(r.sum() - months.max()) if len(months) else 0.0
        wd = pd.DatetimeIndex(t["entry_time"]).tz_convert(tz).dayofweek
        by_wd = pd.Series(net).groupby(wd).sum()
        pos = by_wd[by_wd > 0]
        out["max_weekday_profit_share"] = float(pos.max() / pos.sum()) if len(pos) and total > 0 else 1.0
        if regimes is not None:
            rg = regimes.to_numpy()[t["signal_i"].to_numpy()]
            by_rg = pd.Series(net).groupby(rg).sum()
            pos_r = by_rg[by_rg > 0]
            out["regime_profit"] = {str(int(k)): float(v) for k, v in by_rg.items() if np.isfinite(k)}  # type: ignore[call-overload]
            out["max_regime_profit_share"] = float(pos_r.max() / pos_r.sum()) if len(pos_r) and total > 0 else 1.0
    return out


def stressed_costs(c: CostModel, mult: float) -> CostModel:
    return CostModel(spread_bps=c.spread_bps * mult, commission_bps=c.commission_bps * mult,
                     slippage_bps=c.slippage_bps * mult, latency_bars=c.latency_bars,
                     use_data_spread=c.use_data_spread)
