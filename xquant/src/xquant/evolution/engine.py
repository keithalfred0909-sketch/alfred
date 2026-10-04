"""EVOLUTION ENGINE: genetic search over strategy genomes, on TRAIN only.

Fitness is deliberately not "profit". It rewards consistency across chronological folds inside TRAIN
and penalises complexity, drawdown, too few trades and extreme parameters:

    fitness = 0.35*SR_train + 0.35*median(SR_fold) - 0.25*std(SR_fold) + 0.10*frac_folds_positive
              + 0.05*tanh(PF-1) + 0.05*tanh(expectancy/cost)
              - 0.08*(complexity-1) - 1.0*max(0, MDD-0.25) - extreme-parameter penalty
    fitness = -inf if trades < min_trades

Parameter sensitivity is applied to the elite: the final ranking of a generation's best uses the mean
fitness of the genome and its one-step neighbours, so knife-edge optima lose to plateaus.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np

from xquant.errors import BudgetExceeded
from xquant.logging_utils import get_logger
from xquant.strategy.evaluator import EvalContext
from xquant.strategy.genome import HOLDS, STOPS, TAILS, TAKES, Condition, Genome, neighbours, random_genome

log = get_logger("evolution")


@dataclass
class Individual:
    genome: Genome
    fitness: float = -math.inf
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionResult:
    population: list[Individual]
    best_history: list[float]
    generations: int
    evaluations: int
    stop_reason: str
    elite: list[Individual]
    sr_trials: list[float]  # train Sharpe of every evaluated genome (deflated Sharpe input)


class EvolutionEngine:
    def __init__(self, ctx: EvalContext, train: slice, features: list[str], categorical: dict[str, list[float]],
                 seeds: list[Genome], rng: np.random.Generator, population: int, generations: int,
                 patience: int, max_complexity: int, min_trades: int, n_regimes: int = 0, folds: int = 4,
                 min_trades_per_day: float = 0.0,
                 deadline: float | None = None) -> None:
        self.ctx, self.train = ctx, train
        self.features, self.categorical = features, categorical
        self.seeds, self.rng = seeds, rng
        self.pop_size, self.max_gen, self.patience = population, generations, patience
        self.max_cond = max(1, max_complexity - 1)
        self.max_complexity, self.min_trades = max_complexity, min_trades
        idx = ctx.market.index[train]
        self.train_days = max((idx[-1] - idx[0]).total_seconds() / 86400.0, 1.0)
        self.min_trades = max(min_trades, int(min_trades_per_day * self.train_days * 5 / 7))  # trading days
        self.n_regimes, self.folds = n_regimes, folds
        self.deadline = deadline
        self.cache: dict[str, Individual] = {}
        self.sr_trials: list[float] = []
        a, b = train.start or 0, train.stop
        edges = np.linspace(a, b, folds + 1).astype(int)
        self.fold_slices = [slice(int(edges[i]), int(edges[i + 1])) for i in range(folds)]
        per_fill = (ctx.costs.spread_bps / 2 + ctx.costs.commission_bps + ctx.costs.slippage_bps) * 1e-4
        self.round_trip = 2 * per_fill

    # ---- fitness ---------------------------------------------------------------------------------
    def evaluate(self, g: Genome) -> Individual:
        key = g.key()
        if key in self.cache:
            return self.cache[key]
        if self.deadline and time.time() > self.deadline:
            raise BudgetExceeded("compute time budget exhausted during evolution")
        ind = Individual(g)
        res = self.ctx.backtest(g, self.train, self.train)
        met = res.metrics
        self.sr_trials.append(met.sharpe)
        if met.trades < self.min_trades:
            ind.fitness = -10.0 + met.trades / max(self.min_trades, 1)
            ind.details = {"reason": "too few trades", "trades": met.trades, "required": self.min_trades}
            self.cache[key] = ind
            return ind
        rets = res.returns.to_numpy()
        a = self.train.start or 0
        fold_sr = []
        for fs in self.fold_slices:
            r = rets[fs.start - a:fs.stop - a]
            sd = r.std(ddof=1)
            fold_sr.append(float(r.mean() / sd * math.sqrt(self.ctx.market.ppy)) if sd > 0 else 0.0)
        fsr = np.array(fold_sr)
        pf = met.profit_factor if math.isfinite(met.profit_factor) else 5.0
        extreme = sum(0.05 for c in g.conditions if c.side != "eq" and c.q <= 0.05) + (0.05 if g.hold == 1 else 0.0)
        fit = (0.35 * met.sharpe + 0.35 * float(np.median(fsr)) - 0.25 * float(fsr.std())
               + 0.10 * float((fsr > 0).mean()) + 0.05 * math.tanh(pf - 1)
               + 0.05 * math.tanh(met.expectancy / self.round_trip)
               - 0.08 * (g.complexity - 1) - 1.0 * max(0.0, met.max_drawdown - 0.25) - extreme)
        ind.fitness = float(fit)
        ind.details = {"train": met.to_dict(), "fold_sharpe": fold_sr}
        self.cache[key] = ind
        return ind

    def robust_fitness(self, ind: Individual) -> float:
        """Mean fitness of the genome and its neighbours (penalises knife-edge parameters)."""
        nb = neighbours(ind.genome)
        vals = [ind.fitness] + [self.evaluate(n).fitness for n in nb]
        ind.details["neighbour_fitness"] = vals[1:]
        return float(np.mean(vals))

    # ---- operators -------------------------------------------------------------------------------
    def _random(self) -> Genome:
        return random_genome(self.rng, self.features, self.categorical, self.max_cond, self.n_regimes)

    def mutate(self, g: Genome) -> Genome:
        r = self.rng.random()
        conds = list(g.conditions)
        if r < 0.25 and conds:
            i = int(self.rng.integers(len(conds)))
            c = conds[i]
            if c.side != "eq":
                conds[i] = replace(c, q=float(self.rng.choice(TAILS)), side=str(self.rng.choice(["low", "high"])))
            g = replace(g, conditions=tuple(conds))
        elif r < 0.40 and conds:
            i = int(self.rng.integers(len(conds)))
            f = str(self.rng.choice(self.features))
            conds[i] = (Condition(f, "eq", float(self.rng.choice(self.categorical[f]))) if f in self.categorical
                        else Condition(f, conds[i].side if conds[i].side != "eq" else "low", conds[i].q if conds[i].side != "eq" else 0.1))
            g = replace(g, conditions=tuple(conds))
        elif r < 0.55:
            g = replace(g, hold=int(self.rng.choice(HOLDS)))
        elif r < 0.65:
            g = replace(g, stop=self.rng.choice(STOPS))  # type: ignore[arg-type]
        elif r < 0.72:
            g = replace(g, take=self.rng.choice(TAKES))  # type: ignore[arg-type]
        elif r < 0.82 and len(conds) < self.max_cond:
            extra = random_genome(self.rng, self.features, self.categorical, 1, 0).conditions[0]
            if extra.feature not in {c.feature for c in conds}:
                g = replace(g, conditions=tuple(conds + [extra]))
        elif r < 0.90 and len(conds) > 1:
            conds.pop(int(self.rng.integers(len(conds))))
            g = replace(g, conditions=tuple(conds))
        elif r < 0.95:
            g = replace(g, direction=-g.direction)
        elif self.n_regimes:
            g = replace(g, regime=None if g.regime is not None else int(self.rng.integers(self.n_regimes)))
        return replace(g, origin="mutation")

    def crossover(self, a: Genome, b: Genome) -> Genome:
        pool = list({c.feature: c for c in a.conditions + b.conditions}.values())
        self.rng.shuffle(pool)
        n = int(self.rng.integers(1, min(len(pool), self.max_cond) + 1))
        src = a if self.rng.random() < 0.5 else b
        return Genome(conditions=tuple(pool[:n]), direction=src.direction,
                      hold=(a if self.rng.random() < 0.5 else b).hold, stop=(a if self.rng.random() < 0.5 else b).stop,
                      take=(a if self.rng.random() < 0.5 else b).take, regime=src.regime, origin="crossover")

    def _tournament(self, pop: list[Individual], k: int = 3) -> Individual:
        picks = self.rng.choice(len(pop), size=min(k, len(pop)), replace=False)
        return max((pop[i] for i in picks), key=lambda x: x.fitness)

    def _valid(self, g: Genome) -> bool:
        return 1 <= len(g.conditions) and g.complexity <= self.max_complexity

    # ---- main loop -------------------------------------------------------------------------------
    def run(self) -> EvolutionResult:
        genomes = [s for s in self.seeds if self._valid(s)][: self.pop_size // 2]
        while len(genomes) < self.pop_size:
            genomes.append(self._random())
        pop = [self.evaluate(g) for g in genomes]
        best_hist: list[float] = []
        best, stale, gen, stop_reason = -math.inf, 0, 0, "max generations"
        try:
            for gen in range(1, self.max_gen + 1):
                pop.sort(key=lambda x: -x.fitness)
                cur = pop[0].fitness
                best_hist.append(cur)
                if cur > best + 1e-3:
                    best, stale = cur, 0
                else:
                    stale += 1
                if stale >= self.patience:
                    stop_reason = f"no improvement for {self.patience} generations"
                    break
                n_elite = max(2, self.pop_size // 10)
                nxt = pop[:n_elite]
                seen = {i.genome.key() for i in nxt}
                attempts = 0
                while len(nxt) < self.pop_size and attempts < self.pop_size * 10:
                    attempts += 1
                    r = self.rng.random()
                    if r < 0.45:
                        child = self.crossover(self._tournament(pop).genome, self._tournament(pop).genome)
                        if self.rng.random() < 0.3:
                            child = self.mutate(child)
                    elif r < 0.90:
                        child = self.mutate(self._tournament(pop).genome)
                    else:
                        child = self._random()  # immigration keeps diversity
                    if not self._valid(child) or child.key() in seen:
                        continue
                    seen.add(child.key())
                    nxt.append(self.evaluate(child))
                pop = nxt
                log.debug("gen %d best %.3f evaluated %d", gen, cur, len(self.cache))
        except BudgetExceeded as exc:
            stop_reason = str(exc)
        pop.sort(key=lambda x: -x.fitness)
        elite = [i for i in pop if i.fitness > 0][:20]
        for ind in elite:
            ind.details["robust_fitness"] = self.robust_fitness(ind)
        elite.sort(key=lambda x: -x.details["robust_fitness"])
        log.info("evolution: %d generations, %d genomes evaluated, best fitness %.3f, %d positive elite (%s)",
                 gen, len(self.cache), pop[0].fitness if pop else float("nan"), len(elite), stop_reason)
        return EvolutionResult(pop, best_hist, gen, len(self.cache), stop_reason, elite, self.sr_trials)
