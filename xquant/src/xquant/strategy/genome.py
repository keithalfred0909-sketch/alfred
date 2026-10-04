"""STRATEGY GENERATOR: the strategy genome and its translation into entry signals.

A strategy is a conjunction of tail conditions on discovered features, a direction, a holding period
and optional volatility-scaled stop / take-profit and regime filter. Nothing in the vocabulary is a
pre-packaged trading system: conditions come from the feature/hypothesis engines.

Thresholds are *fitted* (quantiles on a fit window) and stored separately from the genome so that
walk-forward analysis can re-fit them on each in-sample window.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from typing import Any

import numpy as np
import pandas as pd

from xquant.hypothesis.engine import Hypothesis

HOLDS = [1, 2, 3, 5, 8, 10, 15, 20]
STOPS: list[float | None] = [None, 0.5, 1.0, 1.5, 2.0]
TAKES: list[float | None] = [None, 1.0, 1.5, 2.0, 3.0]
TAILS = [0.05, 0.1, 0.15, 0.2, 0.3]
TRAILS: list[float | None] = [None, 0.5, 1.0, 1.5, 2.0]


@dataclass(frozen=True)
class Condition:
    feature: str
    side: str  # low | high | eq
    q: float  # tail size (or category value for eq)

    def key(self) -> str:
        return f"{self.feature}:{self.side}:{self.q:g}"


@dataclass(frozen=True)
class Genome:
    conditions: tuple[Condition, ...]
    direction: int
    hold: int
    stop: float | None = None
    take: float | None = None
    regime: int | None = None
    origin: str = "random"
    trail: float | None = None

    def key(self) -> str:
        conds = "&".join(sorted(c.key() for c in self.conditions))
        base = f"{conds}|d{self.direction}|h{self.hold}|s{self.stop}|t{self.take}|r{self.regime}"
        return base if self.trail is None else f"{base}|tr{self.trail}"  # old keys unchanged

    @property
    def signature(self) -> str:
        return hashlib.sha1(self.key().encode()).hexdigest()[:16]

    @property
    def complexity(self) -> int:
        return (len(self.conditions) + (self.stop is not None) + (self.take is not None) + (self.regime is not None)
                + (self.trail is not None))

    def describe(self) -> str:
        cs = " AND ".join(f"{c.feature} {'in bottom' if c.side == 'low' else 'in top' if c.side == 'high' else '=='} "
                          f"{c.q:.0%}" if c.side != "eq" else f"{c.feature} == {c.q:g}" for c in self.conditions)
        reg = f" AND regime == {self.regime}" if self.regime is not None else ""
        ex = f"exit after {self.hold} bars" if self.hold else "exit at the close of the entry bar"
        if self.stop is not None:
            ex += f", stop {self.stop} x vol x sqrt(hold)"
        if self.take is not None:
            ex += f", take-profit {self.take} x vol x sqrt(hold)"
        if self.trail is not None:
            ex += f", trailing stop {self.trail} x vol x sqrt(hold) from best close"
        return f"{'LONG' if self.direction > 0 else 'SHORT'} when {cs}{reg}; {ex}"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["conditions"] = [asdict(c) for c in self.conditions]
        return d

    @staticmethod
    def from_dict(d: dict[str, Any]) -> Genome:
        return Genome(conditions=tuple(Condition(**c) for c in d["conditions"]), direction=int(d["direction"]),
                      hold=int(d["hold"]), stop=d.get("stop"), take=d.get("take"), regime=d.get("regime"),
                      origin=d.get("origin", "random"), trail=d.get("trail"))


@dataclass
class FittedStrategy:
    genome: Genome
    thresholds: dict[str, float] = field(default_factory=dict)  # condition key -> threshold

    def to_dict(self) -> dict[str, Any]:
        return {"genome": self.genome.to_dict(), "thresholds": self.thresholds}


def fit_thresholds(genome: Genome, features: dict[str, pd.Series], fit: slice) -> FittedStrategy:
    th: dict[str, float] = {}
    for c in genome.conditions:
        x = features[c.feature].iloc[fit].dropna()
        if c.side == "low":
            th[c.key()] = float(x.quantile(c.q)) if len(x) else float("nan")
        elif c.side == "high":
            th[c.key()] = float(x.quantile(1 - c.q)) if len(x) else float("nan")
        else:
            th[c.key()] = c.q
    return FittedStrategy(genome, th)


def entry_signal(fs: FittedStrategy, features: dict[str, pd.Series], regimes: pd.Series | None) -> np.ndarray:
    n = len(next(iter(features.values())))
    sig = np.ones(n, dtype=bool)
    for c in fs.genome.conditions:
        x = features[c.feature].to_numpy()
        t = fs.thresholds[c.key()]
        with np.errstate(invalid="ignore"):
            if c.side == "low":
                sig &= x <= t
            elif c.side == "high":
                sig &= x >= t
            else:
                sig &= x == t
        sig &= np.isfinite(x)
    if fs.genome.regime is not None:
        if regimes is None:
            return np.zeros(n, dtype=bool)
        sig &= regimes.to_numpy() == fs.genome.regime
    return sig


def genome_from_hypothesis(h: Hypothesis) -> Genome:
    return Genome(conditions=(Condition(h.feature, h.side, h.q if h.side != "eq" else h.threshold),),
                  direction=h.direction or 1, hold=min(HOLDS, key=lambda x: abs(x - h.horizon)),
                  regime=h.regime, origin=h.id or h.signature)


def random_genome(rng: np.random.Generator, features: list[str], categorical: dict[str, list[float]],
                  max_conditions: int, n_regimes: int) -> Genome:
    n_cond = int(rng.integers(1, max_conditions + 1))
    conds = []
    for f in rng.choice(features, size=min(n_cond, len(features)), replace=False):
        f = str(f)
        if f in categorical:
            conds.append(Condition(f, "eq", float(rng.choice(categorical[f]))))
        else:
            conds.append(Condition(f, str(rng.choice(["low", "high"])), float(rng.choice(TAILS))))
    return Genome(conditions=tuple(conds), direction=int(rng.choice([-1, 1])), hold=int(rng.choice(HOLDS)),
                  stop=rng.choice(STOPS) if rng.random() < 0.3 else None,  # type: ignore[arg-type]
                  take=rng.choice(TAKES) if rng.random() < 0.2 else None,  # type: ignore[arg-type]
                  regime=int(rng.integers(n_regimes)) if n_regimes and rng.random() < 0.15 else None,
                  trail=rng.choice(TRAILS[1:]) if rng.random() < 0.2 else None)  # type: ignore[arg-type]


def neighbours(g: Genome, scale: float = 0.25) -> list[Genome]:
    """Parameter-perturbed variants used for sensitivity analysis (one parameter at a time)."""
    out: list[Genome] = []
    for i, c in enumerate(g.conditions):
        if c.side == "eq":
            continue
        for f in (1 - scale, 1 + scale):
            q = float(np.clip(c.q * f, 0.02, 0.45))
            conds = list(g.conditions)
            conds[i] = replace(c, q=q)
            out.append(replace(g, conditions=tuple(conds)))
    for f in (1 - scale, 1 + scale):
        h = max(1, int(round(g.hold * f)))
        if h != g.hold:
            out.append(replace(g, hold=h))
        else:
            out.append(replace(g, hold=g.hold + (1 if f > 1 else -1) if g.hold > 1 or f > 1 else g.hold))
    for attr in ("stop", "take", "trail"):
        v = getattr(g, attr)
        if v is not None:
            for f in (1 - scale, 1 + scale):
                out.append(replace(g, **{attr: round(v * f, 3)}))
    return [n for n in out if n.key() != g.key()]


def genome_json(g: Genome) -> str:
    return json.dumps(g.to_dict(), sort_keys=True)
