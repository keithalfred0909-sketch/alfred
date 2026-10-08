"""OVERFITTING DETECTOR.

* Deflated Sharpe Ratio: is the selected strategy's in-sample Sharpe better than the expected best of
  N zero-skill trials? N = every backtest ever run on this asset/dataset (from the research memory).
* Probability of Backtest Overfitting (CSCV, Bailey et al.): across a set of candidates, how often is
  the in-sample winner below the median out of sample?
* IS->OOS degradation.
"""

from __future__ import annotations

import itertools
import math
from typing import Any

import numpy as np

from xquant.stats import deflated_sharpe, expected_max_sharpe


def pbo_cscv(returns_matrix: np.ndarray, n_blocks: int = 10) -> dict[str, Any]:
    """``returns_matrix``: T x N per-bar returns of N candidate strategies over the same period."""
    T, N = returns_matrix.shape
    if N < 4 or T < n_blocks * 20:
        return {"status": "INSUFFICIENT DATA", "candidates": N}
    blocks = np.array_split(np.arange(T), n_blocks)
    logits = []
    for combo in itertools.combinations(range(n_blocks), n_blocks // 2):
        is_idx = np.concatenate([blocks[i] for i in combo])
        oos_idx = np.concatenate([blocks[i] for i in range(n_blocks) if i not in combo])
        is_r, oos_r = returns_matrix[is_idx], returns_matrix[oos_idx]
        is_sr = is_r.mean(0) / (is_r.std(0) + 1e-12)
        oos_sr = oos_r.mean(0) / (oos_r.std(0) + 1e-12)
        best = int(np.argmax(is_sr))
        rank = (oos_sr < oos_sr[best]).sum() + 0.5 * ((oos_sr == oos_sr[best]).sum() - 1)
        w = (rank + 0.5) / N
        w = min(max(w, 1e-6), 1 - 1e-6)
        logits.append(math.log(w / (1 - w)))
    lg = np.array(logits)
    return {"status": "OK", "pbo": float((lg <= 0).mean()), "combinations": len(lg), "candidates": N}


def deflated_sharpe_report(train_returns: np.ndarray, n_trials: int, var_sr_annual: float, ppy: float) -> dict[str, Any]:
    """Deflated Sharpe with the *null* variance of the Sharpe estimator (1/T per period).

    The cross-sectional variance of a genetic population's Sharpe ratios is not a valid null: when a real
    effect exists the population converges on it, inflating the variance and penalising exactly the true
    signal (verified by the positive-control integration test). Under H0 each trial's per-period Sharpe
    estimate has variance ~1/T, and N counts every backtest ever run on this dataset (conservative, since
    GA trials are correlated). The empirical dispersion is reported for information only.
    """
    r = np.asarray(train_returns, dtype=float)
    t = int(np.isfinite(r).sum())
    var0 = 1.0 / max(t - 1, 1)
    sr0 = expected_max_sharpe(max(n_trials, 1), var0)
    return {"n_trials": int(n_trials), "null_sr_benchmark_annual": float(sr0 * math.sqrt(ppy)),
            "sr_trials_std_annual": float(math.sqrt(max(var_sr_annual, 0.0))),
            "dsr": float(deflated_sharpe(r, max(n_trials, 1), var0))}


def degradation(is_sharpe: float, oos_sharpe: float) -> float:
    return float(oos_sharpe / is_sharpe) if is_sharpe > 0 else float("nan")
