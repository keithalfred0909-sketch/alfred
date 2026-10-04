"""Statistical toolkit shared by every engine.

Conventions: two-sided p-values; serially dependent data (overlapping forward returns, volatility
clustering) is handled with Newey-West HAC standard errors; multiple testing with Benjamini-Hochberg.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats as sps


@dataclass(frozen=True)
class TestResult:
    statistic: float
    p_value: float
    effect: float  # estimate in natural units (e.g. mean difference)
    n: int

    @property
    def valid(self) -> bool:
        return math.isfinite(self.p_value)


NAN_RESULT = TestResult(float("nan"), float("nan"), float("nan"), 0)


def newey_west_se(x: np.ndarray, lags: int | None = None) -> float:
    """HAC standard error of the mean of ``x`` (Bartlett kernel)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 3:
        return float("nan")
    if lags is None:
        lags = int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    u = x - x.mean()
    gamma0 = float(u @ u) / n
    s = gamma0
    for k in range(1, min(lags, n - 1) + 1):
        w = 1.0 - k / (lags + 1.0)
        s += 2.0 * w * float(u[k:] @ u[:-k]) / n
    return math.sqrt(max(s, 1e-300) / n)


def hac_mean_test(x: np.ndarray, lags: int | None = None, mu0: float = 0.0) -> TestResult:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 5:
        return NAN_RESULT
    se = newey_west_se(x, lags)
    if not (se > 0):
        return NAN_RESULT
    t = (x.mean() - mu0) / se
    return TestResult(float(t), float(2 * sps.norm.sf(abs(t))), float(x.mean() - mu0), len(x))


def hac_conditional_diff(y: np.ndarray, cond: np.ndarray, lags: int | None = None) -> TestResult:
    """Test E[y | cond] - E[y | not cond] = 0 by OLS of y on [1, cond] with HAC covariance.

    Robust to the overlap of multi-bar forward returns when ``lags`` >= horizon - 1.
    """
    y = np.asarray(y, dtype=float)
    c = np.asarray(cond, dtype=bool)
    ok = np.isfinite(y)
    y, c = y[ok], c[ok]
    n, n1 = len(y), int(c.sum())
    if n1 < 5 or n - n1 < 5:
        return TestResult(float("nan"), float("nan"), float("nan"), n1)
    X = np.column_stack([np.ones(n), c.astype(float)])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    if lags is None:
        lags = int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for k in range(1, min(lags, n - 1) + 1):
        w = 1.0 - k / (lags + 1.0)
        G = Xu[k:].T @ Xu[:-k]
        S += w * (G + G.T)
    cov = XtX_inv @ S @ XtX_inv
    se = math.sqrt(max(cov[1, 1], 1e-300))
    t = beta[1] / se
    return TestResult(float(t), float(2 * sps.norm.sf(abs(t))), float(beta[1]), n1)


def benjamini_hochberg(pvals: list[float] | np.ndarray, alpha: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    """Return (reject mask, adjusted q-values). NaN p-values are never rejected."""
    p = np.asarray(pvals, dtype=float)
    q = np.full_like(p, np.nan)
    ok = np.isfinite(p)
    m = int(ok.sum())
    if m == 0:
        return np.zeros_like(p, dtype=bool), q
    pv = p[ok]
    order = np.argsort(pv)
    ranked = pv[order] * m / (np.arange(m) + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.clip(adj, 0, 1)
    out = np.empty(m)
    out[order] = adj
    q[ok] = out
    return (q <= alpha) & ok, q


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def variance_ratio_test(r: np.ndarray, q: int) -> TestResult:
    """Lo-MacKinlay variance ratio with heteroskedasticity-robust z*. VR>1 momentum, VR<1 reversion."""
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 10 * q:
        return NAN_RESULT
    mu = r.mean()
    d = r - mu
    var1 = float(d @ d) / (n - 1)
    rq = np.convolve(r, np.ones(q), mode="valid")
    m = q * (n - q + 1) * (1 - q / n)
    varq = float(((rq - q * mu) ** 2).sum()) / m
    vr = varq / var1
    d2 = d * d
    denom = float(d2.sum()) ** 2
    theta = 0.0
    for j in range(1, q):
        delta = float((d2[j:] * d2[:-j]).sum()) / denom * n
        theta += (2 * (q - j) / q) ** 2 * delta
    z = (vr - 1) / math.sqrt(theta / n) if theta > 0 else float("nan")
    return TestResult(float(z), float(2 * sps.norm.sf(abs(z))), float(vr), n)


def ljung_box(x: np.ndarray, lags: int) -> TestResult:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < lags + 10:
        return NAN_RESULT
    u = x - x.mean()
    den = float(u @ u)
    acf = np.array([float(u[k:] @ u[:-k]) / den for k in range(1, lags + 1)])
    qstat = n * (n + 2) * float(np.sum(acf**2 / (n - np.arange(1, lags + 1))))
    return TestResult(qstat, float(sps.chi2.sf(qstat, lags)), float(acf[0]), n)


def autocorr(x: np.ndarray, lags: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    u = x - x.mean()
    den = float(u @ u)
    return np.array([float(u[k:] @ u[:-k]) / den for k in range(1, lags + 1)])


def arch_lm(r: np.ndarray, lags: int = 5) -> TestResult:
    """Engle ARCH-LM: regress r_t^2 on its lags; n*R^2 ~ chi2(lags) under no ARCH effects."""
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    e2 = (r - r.mean()) ** 2
    n = len(e2) - lags
    if n < 50:
        return NAN_RESULT
    Y = e2[lags:]
    X = np.column_stack([np.ones(n)] + [e2[lags - k:-k] for k in range(1, lags + 1)])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    r2 = 1 - float(resid @ resid) / float(((Y - Y.mean()) ** 2).sum())
    stat = n * r2
    return TestResult(stat, float(sps.chi2.sf(stat, lags)), r2, n)


def runs_test(signs: np.ndarray) -> TestResult:
    """Wald-Wolfowitz runs test on a +/- sequence. Fewer runs than expected = persistence."""
    s = np.asarray(signs)
    s = s[s != 0]
    n1, n2 = int((s > 0).sum()), int((s < 0).sum())
    n = n1 + n2
    if n1 < 10 or n2 < 10:
        return NAN_RESULT
    runs = 1 + int((s[1:] != s[:-1]).sum())
    mu = 2 * n1 * n2 / n + 1
    var = (mu - 1) * (mu - 2) / (n - 1)
    z = (runs - mu) / math.sqrt(var)
    return TestResult(float(z), float(2 * sps.norm.sf(abs(z))), float(runs / mu), n)


def stationary_bootstrap_indices(n: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary bootstrap index sequence of length n (vectorised).

    Each position starts a new block with probability 1/mean_block (always at t=0); otherwise it continues
    the previous block (index + 1, wrapping around)."""
    restart = rng.random(n) < 1.0 / mean_block
    restart[0] = True
    starts = rng.integers(0, n, size=n)
    t = np.arange(n)
    last = np.maximum.accumulate(np.where(restart, t, 0))
    return ((starts[last] + (t - last)) % n).astype(np.int64)


def sharpe(returns: np.ndarray, periods_per_year: float) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) < 2 or r.std(ddof=1) == 0:
        return 0.0
    return float(r.mean() / r.std(ddof=1) * math.sqrt(periods_per_year))


def probabilistic_sharpe(sr: float, n: int, skew: float, kurt: float, sr_benchmark: float = 0.0) -> float:
    """PSR (Bailey & Lopez de Prado). ``sr`` and benchmark are per-period (not annualised); kurt is raw."""
    if n < 3:
        return float("nan")
    den = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr * sr, 1e-12))
    return float(sps.norm.cdf((sr - sr_benchmark) * math.sqrt(n - 1) / den))


def expected_max_sharpe(n_trials: int, var_trials: float) -> float:
    """Expected maximum per-period Sharpe among ``n_trials`` independent zero-skill trials."""
    if n_trials < 2:
        return 0.0
    g = 0.5772156649
    z1 = sps.norm.ppf(1 - 1.0 / n_trials)
    z2 = sps.norm.ppf(1 - 1.0 / (n_trials * math.e))
    return float(math.sqrt(max(var_trials, 0.0)) * ((1 - g) * z1 + g * z2))


def deflated_sharpe(returns: np.ndarray, n_trials: int, var_trials_sr: float) -> float:
    """Deflated Sharpe Ratio: probability that the true Sharpe exceeds the best of ``n_trials`` noise
    strategies. Inputs are per-period returns and the variance of per-period Sharpes across trials."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) < 10 or r.std(ddof=1) == 0:
        return 0.0
    sr = r.mean() / r.std(ddof=1)
    sr0 = expected_max_sharpe(n_trials, var_trials_sr)
    return probabilistic_sharpe(sr, len(r), float(sps.skew(r)), float(sps.kurtosis(r, fisher=False)), sr0)


def forward_returns(log_close: pd.Series, h: int) -> pd.Series:
    """Log return from bar t to bar t+h. Used ONLY as a label, never as a feature."""
    return log_close.shift(-h) - log_close
