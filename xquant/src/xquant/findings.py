"""A ``Finding`` is the unit of output of the exploratory engines (market, macro, news).

Findings are tested on TRAIN, corrected for multiple testing within their batch, and the significant
ones are re-tested on VALIDATION ("replication"). Only replicated findings are called discoveries.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from xquant.stats import TestResult, benjamini_hochberg


@dataclass
class Finding:
    engine: str
    category: str
    name: str
    description: str
    statistic: float = float("nan")
    p_value: float = float("nan")
    effect: float = float("nan")
    n: int = 0
    period: str = ""
    q_value: float = float("nan")
    significant: bool = False
    replication_p: float = float("nan")
    replication_effect: float = float("nan")
    replicated: bool | None = None
    status: str = "TESTED"  # TESTED | DISCOVERY | NOT_SIGNIFICANT | NOT_REPLICATED | INSUFFICIENT DATA | DESCRIPTIVE
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_test(cls, engine: str, category: str, name: str, description: str, res: TestResult,
                  period: str, **details: Any) -> Finding:
        return cls(engine=engine, category=category, name=name, description=description,
                   statistic=res.statistic, p_value=res.p_value, effect=res.effect, n=res.n,
                   period=period, details=details)

    @classmethod
    def insufficient(cls, engine: str, category: str, name: str, reason: str) -> Finding:
        return cls(engine=engine, category=category, name=name, description=reason, status="INSUFFICIENT DATA")

    @classmethod
    def descriptive(cls, engine: str, category: str, name: str, description: str, period: str,
                    **details: Any) -> Finding:
        return cls(engine=engine, category=category, name=name, description=description, period=period,
                   status="DESCRIPTIVE", details=details)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, float) and not math.isfinite(v):
                d[k] = None
        return d


def apply_fdr(findings: list[Finding], alpha: float) -> None:
    testable = [f for f in findings if f.status == "TESTED" and math.isfinite(f.p_value)]
    if not testable:
        return
    rej, q = benjamini_hochberg([f.p_value for f in testable], alpha)
    for f, r, qq in zip(testable, rej, q, strict=True):
        f.q_value = float(qq)
        f.significant = bool(r)
        f.status = "SIGNIFICANT_TRAIN" if r else "NOT_SIGNIFICANT"


def replicate(findings: list[Finding], retest: Callable[[Finding], TestResult | None], alpha: float = 0.05) -> None:
    """Re-run significant findings on held-out data. Replication requires same sign and p < alpha
    (one test per finding, so alpha is Bonferroni-corrected over the number of replications)."""
    sig = [f for f in findings if f.status == "SIGNIFICANT_TRAIN"]
    if not sig:
        return
    a = alpha / len(sig)
    for f in sig:
        res = retest(f)
        if res is None or not res.valid:
            f.replicated, f.status = None, "UNREPLICABLE"
            continue
        f.replication_p, f.replication_effect = res.p_value, res.effect
        same_sign = np.sign(res.effect) == np.sign(f.effect)
        f.replicated = bool(same_sign and res.p_value < a)
        f.status = "DISCOVERY" if f.replicated else "NOT_REPLICATED"
