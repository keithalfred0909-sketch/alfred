"""HYPOTHESIS ENGINE.

A hypothesis has the form

    "When FEATURE is in its LOW/HIGH q-tail [and REGIME = k], the next-H-bar return differs from the
     baseline (all other bars)."

Thresholds are quantiles estimated on the DISCOVERY part of TRAIN. Lifecycle:

    DISCOVERED  -> generated, not tested yet
    TESTING     -> tested on DISCOVERY; BH-FDR across every hypothesis of the batch
    VALIDATION  -> survived FDR and replicated (same sign, p<0.05, min effect) on CONFIRMATION
    REJECTED    -> did not survive FDR on DISCOVERY
    OVERFIT     -> significant on DISCOVERY, failed on CONFIRMATION
    ROBUST      -> a strategy built on it survived the full adversarial pipeline and TEST
    DEAD        -> retired (line stopped / superseded)

``confidence`` is reported as 1 - q (BH-adjusted p-value). It is a significance summary, not the
probability that the hypothesis is true.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from xquant.features.library import CATEGORICAL, Expr, evaluate
from xquant.logging_utils import get_logger
from xquant.stats import benjamini_hochberg, forward_returns, hac_conditional_diff

log = get_logger("hypothesis")

STATES = ("DISCOVERED", "TESTING", "VALIDATION", "ROBUST", "REJECTED", "OVERFIT", "DEAD")


@dataclass
class Hypothesis:
    feature: str
    side: str  # low | high | eq (categorical value)
    q: float  # tail quantile (low: x <= Q(q); high: x >= Q(1-q)); for eq: the category value
    horizon: int
    regime: int | None = None
    threshold: float = float("nan")
    id: str = ""
    complexity: int = 1
    period: str = ""
    sample: int = 0
    baseline: float = float("nan")  # mean forward return on other bars
    result: float = float("nan")  # mean forward return when the condition holds
    effect: float = float("nan")
    effect_size: float = float("nan")  # effect / std(forward return)
    p_value: float = float("nan")
    q_value: float = float("nan")
    confirm_effect: float = float("nan")
    confirm_p: float = float("nan")
    status: str = "DISCOVERED"
    notes: list[str] = field(default_factory=list)

    @property
    def signature(self) -> str:
        blob = json.dumps([self.feature, self.side, round(self.q, 4), self.horizon, self.regime])
        return hashlib.sha1(blob.encode()).hexdigest()[:16]

    @property
    def direction(self) -> int:
        return int(np.sign(self.effect)) if math.isfinite(self.effect) else 0

    @property
    def confidence(self) -> float:
        return 1.0 - self.q_value if math.isfinite(self.q_value) else float("nan")

    def describe(self) -> str:
        if self.side == "eq":
            cond = f"{self.feature} == {self.q:g}"
        else:
            cond = f"{self.feature} {'<=' if self.side == 'low' else '>='} {self.threshold:.4g} " \
                   f"({'bottom' if self.side == 'low' else 'top'} {self.q:.0%})"
        reg = f" and regime={self.regime}" if self.regime is not None else ""
        return f"When {cond}{reg}, next {self.horizon}-bar return differs from baseline"

    def condition(self, x: pd.Series) -> pd.Series:
        if self.side == "low":
            return x <= self.threshold
        if self.side == "high":
            return x >= self.threshold
        return x == self.q

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update(signature=self.signature, description=self.describe(), confidence=self.confidence)
        return {k: (None if isinstance(v, float) and not math.isfinite(v) else v) for k, v in d.items()}


class HypothesisEngine:
    def __init__(self, prims: dict[str, pd.Series], exprs: dict[str, Expr], close: pd.Series,
                 disc: slice, conf: slice, horizons: list[int], quantiles: list[float], alpha: float,
                 min_samples: int, min_effect_size: float, regimes: pd.Series | None = None,
                 cache: dict[str, pd.Series] | None = None, period: str = "") -> None:
        self.prims, self.exprs, self.close = prims, exprs, close
        self.disc, self.conf = disc, conf
        self.horizons = horizons
        self.tails = sorted({round(min(q, 1 - q), 6) for q in quantiles})  # 1-0.8 != 0.2 in floating point
        self.alpha, self.min_samples, self.min_es = alpha, min_samples, min_effect_size
        self.regimes = regimes
        self.cache = cache if cache is not None else {}
        self.period = period
        lc = np.log(close)
        self.fwd = {h: forward_returns(lc, h) for h in horizons}

    def value(self, key: str) -> pd.Series:
        return evaluate(self.exprs[key], self.prims, self.cache)

    def generate(self, features: list[str], with_regimes: bool = False) -> list[Hypothesis]:
        hyps: list[Hypothesis] = []
        for key in features:
            x = self.value(key)
            xd = x.iloc[self.disc].dropna()
            if len(xd) < 200:
                continue
            cx = self.exprs[key].complexity
            if key in CATEGORICAL:
                for val in sorted(xd.unique()):
                    if (xd == val).sum() >= self.min_samples:
                        for h in self.horizons:
                            hyps.append(Hypothesis(key, "eq", float(val), h, threshold=float(val), complexity=cx))
                continue
            for q in self.tails:
                for side, thr in [("low", float(xd.quantile(q))), ("high", float(xd.quantile(1 - q)))]:
                    for h in self.horizons:
                        hyps.append(Hypothesis(key, side, q, h, threshold=thr, complexity=cx))
                        if with_regimes and self.regimes is not None:
                            for k in sorted(self.regimes.dropna().unique().astype(int)):
                                hyps.append(Hypothesis(key, side, q, h, regime=int(k), threshold=thr, complexity=cx + 1))
        return hyps

    def _mask(self, h: Hypothesis) -> np.ndarray:
        cond = h.condition(self.value(h.feature))
        if h.regime is not None and self.regimes is not None:
            cond = cond & (self.regimes == h.regime)
        return cond.fillna(False).to_numpy(dtype=bool)

    def _test(self, h: Hypothesis, sl: slice) -> tuple[float, float, int, float, float, float]:
        y = self.fwd[h.horizon].to_numpy()[sl]
        c = self._mask(h)[sl]
        res = hac_conditional_diff(y, c, lags=h.horizon)
        ok = np.isfinite(y)
        base = float(np.nanmean(y[ok & ~c])) if (ok & ~c).any() else float("nan")
        cond_mean = float(np.nanmean(y[ok & c])) if (ok & c).any() else float("nan")
        sd = float(np.nanstd(y[ok]))
        return res.effect, res.p_value, int((ok & c).sum()), base, cond_mean, sd

    def test(self, hyps: list[Hypothesis]) -> list[Hypothesis]:
        for h in hyps:
            eff, p, n, base, res, sd = self._test(h, self.disc)
            h.effect, h.p_value, h.sample, h.baseline, h.result = eff, p, n, base, res
            h.effect_size = eff / sd if sd > 0 and math.isfinite(eff) else float("nan")
            h.period = self.period
            h.status = "TESTING"
            if n < self.min_samples:
                h.p_value = float("nan")
                h.notes.append(f"sample {n} < {self.min_samples}")
        testable = [h for h in hyps if math.isfinite(h.p_value)]
        rej, q = benjamini_hochberg([h.p_value for h in testable], self.alpha)
        for h, r, qq in zip(testable, rej, q, strict=True):
            h.q_value = float(qq)
            if not r or abs(h.effect_size) < self.min_es:
                h.status = "REJECTED"
                continue
            eff2, p2, n2, *_ = self._test(h, self.conf)
            h.confirm_effect, h.confirm_p = eff2, p2
            ok = math.isfinite(eff2) and np.sign(eff2) == np.sign(h.effect) and p2 < 0.05 and n2 >= self.min_samples // 2
            h.status = "VALIDATION" if ok else "OVERFIT"
        for h in hyps:
            if h.status == "TESTING":
                h.status = "REJECTED"
        n_val = sum(h.status == "VALIDATION" for h in hyps)
        log.info("hypotheses: %d tested, %d significant on discovery, %d confirmed", len(hyps),
                 sum(h.status in ("VALIDATION", "OVERFIT") for h in hyps), n_val)
        return hyps
