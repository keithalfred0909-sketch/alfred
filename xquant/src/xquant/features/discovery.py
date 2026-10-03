"""FEATURE DISCOVERY ENGINE.

TRAIN is split internally into DISCOVERY (first 70%) and CONFIRMATION (last 30%, after an embargo).
VALIDATION/TEST/FINAL are never seen here.

1. candidates = all primitives + random expressions (bounded complexity)
2. on DISCOVERY: rank information coefficient vs forward returns (several horizons), with the sample
   size deflated by the horizon to account for overlap; BH-FDR over every (feature, horizon) pair
3. on CONFIRMATION: same sign and p < 0.05 required
4. complexity control: an expression with complexity > 1 is kept only if its confirmation |IC| beats
   the best of its constituent primitives by a margin

Output: a ranked pool. Primitives that do not pass are still available to the hypothesis engine (which
looks at tails, where linear IC is blind), but are flagged as not informative linearly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as sps

from xquant.features.library import CATEGORICAL, Expr, evaluate, prim, random_expr
from xquant.logging_utils import get_logger
from xquant.stats import benjamini_hochberg, forward_returns

log = get_logger("features")


@dataclass
class FeatureScore:
    key: str
    complexity: int
    horizon: int
    ic_disc: float
    p_disc: float
    ic_conf: float = float("nan")
    p_conf: float = float("nan")
    q_disc: float = float("nan")
    status: str = "CANDIDATE"  # CONFIRMED | REJECTED | NOT_CONFIRMED | TOO_COMPLEX

    def to_dict(self) -> dict[str, Any]:
        return {k: (None if isinstance(v, float) and not math.isfinite(v) else v) for k, v in self.__dict__.items()}


@dataclass
class FeaturePool:
    exprs: dict[str, Expr]
    scores: list[FeatureScore]
    confirmed: list[str] = field(default_factory=list)
    inner_split: tuple[slice, slice] = (slice(0, 0), slice(0, 0))

    def hypothesis_features(self, max_n: int) -> list[str]:
        """Features offered to the hypothesis engine: confirmed first, then primitives."""
        prims = [k for k, e in self.exprs.items() if e.op == "prim"]
        ordered = list(dict.fromkeys(self.confirmed + prims))
        return ordered[:max_n]


def rank_ic(x: np.ndarray, y: np.ndarray, horizon: int) -> tuple[float, float]:
    ok = np.isfinite(x) & np.isfinite(y)
    n = int(ok.sum())
    if n < 100 or np.nanstd(x[ok]) == 0:
        return float("nan"), float("nan")
    ic = float(sps.spearmanr(x[ok], y[ok]).statistic)
    n_eff = max(n / max(horizon, 1), 10)
    t = ic * math.sqrt((n_eff - 2) / max(1e-12, 1 - ic * ic))
    return ic, float(2 * sps.t.sf(abs(t), n_eff - 2))


def inner_train_split(train: slice, embargo: int, frac: float = 0.7) -> tuple[slice, slice]:
    a, b = train.start or 0, train.stop
    cut = a + int((b - a) * frac)
    return slice(a, cut), slice(min(cut + embargo, b), b)


class FeatureDiscovery:
    def __init__(self, prims: dict[str, pd.Series], close: pd.Series, train: slice, embargo: int,
                 horizons: list[int], seed: int, max_features: int, max_complexity: int, alpha: float = 0.05,
                 complexity_margin: float = 0.01) -> None:
        self.prims, self.close, self.train = prims, close, train
        self.horizons = horizons
        self.rng = np.random.default_rng(seed)
        self.max_features, self.max_complexity = max_features, max_complexity
        self.alpha, self.margin = alpha, complexity_margin
        self.disc, self.conf = inner_train_split(train, embargo)
        self.cache: dict[str, pd.Series] = {}

    def candidates(self) -> dict[str, Expr]:
        out = {k: prim(k) for k in self.prims}
        names = list(self.prims)
        tries = 0
        while len(out) < self.max_features and tries < self.max_features * 20:
            tries += 1
            e = random_expr(self.rng, names, self.max_complexity)
            out.setdefault(e.key(), e)
        return out

    def run(self) -> FeaturePool:
        exprs = self.candidates()
        lc = np.log(self.close)
        fwd = {h: forward_returns(lc, h).to_numpy() for h in self.horizons}
        scores: list[FeatureScore] = []
        values: dict[str, np.ndarray] = {}
        for key, e in exprs.items():
            if key in CATEGORICAL:
                continue  # categorical primitives are handled by bucket hypotheses, not linear IC
            try:
                v = evaluate(e, self.prims, self.cache).to_numpy()
            except Exception as exc:
                log.debug("feature %s failed: %s", key, exc)
                continue
            values[key] = v
            for h in self.horizons:
                ic, p = rank_ic(v[self.disc], fwd[h][self.disc], h)
                if math.isfinite(p):
                    scores.append(FeatureScore(key, e.complexity, h, ic, p))
        rej, q = benjamini_hochberg([s.p_disc for s in scores], self.alpha)
        for s, r, qq in zip(scores, rej, q, strict=True):
            s.q_disc = float(qq)
            if not r:
                s.status = "REJECTED"
                continue
            ic2, p2 = rank_ic(values[s.key][self.conf], fwd[s.horizon][self.conf], s.horizon)
            s.ic_conf, s.p_conf = ic2, p2
            s.status = "CONFIRMED" if (math.isfinite(ic2) and np.sign(ic2) == np.sign(s.ic_disc) and p2 < 0.05) else "NOT_CONFIRMED"
        best_prim_ic: dict[tuple[str, int], float] = {
            (s.key, s.horizon): abs(s.ic_conf) if math.isfinite(s.ic_conf) else 0.0 for s in scores if exprs[s.key].op == "prim"}
        for s in scores:
            if s.status == "CONFIRMED" and s.complexity > 1:
                base = max((best_prim_ic.get((p, s.horizon), 0.0) for p in exprs[s.key].primitives()), default=0.0)
                if abs(s.ic_conf) < base + self.margin:
                    s.status = "TOO_COMPLEX"
        confirmed = sorted({s.key for s in scores if s.status == "CONFIRMED"},
                           key=lambda k: -max(abs(s.ic_conf) for s in scores if s.key == k and s.status == "CONFIRMED"))
        log.info("feature discovery: %d expressions, %d (feature,horizon) tests, %d confirmed features",
                 len(exprs), len(scores), len(confirmed))
        return FeaturePool(exprs=exprs, scores=scores, confirmed=confirmed, inner_split=(self.disc, self.conf))
