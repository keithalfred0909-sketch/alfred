"""Shared evaluation context: everything needed to fit and backtest a genome on any window."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from xquant.backtest.engine import BacktestResult, MarketArrays, run_backtest
from xquant.config import CostModel
from xquant.features.library import Expr, evaluate
from xquant.strategy.genome import FittedStrategy, Genome, entry_signal, fit_thresholds


@dataclass
class EvalContext:
    market: MarketArrays
    prims: dict[str, pd.Series]
    exprs: dict[str, Expr]
    costs: CostModel
    regimes: pd.Series | None = None
    cache: dict[str, pd.Series] = field(default_factory=dict)
    evaluations: int = 0  # every backtest counts as a trial (input to the deflated Sharpe ratio)

    def features_for(self, genome: Genome) -> dict[str, pd.Series]:
        return {c.feature: evaluate(self.exprs[c.feature], self.prims, self.cache) for c in genome.conditions}

    def fit(self, genome: Genome, fit_window: slice) -> FittedStrategy:
        return fit_thresholds(genome, self.features_for(genome), fit_window)

    def signal(self, fs: FittedStrategy) -> np.ndarray:
        return entry_signal(fs, self.features_for(fs.genome), self.regimes)

    def backtest(self, genome: Genome, fit_window: slice, eval_window: slice, count: bool = True,
                 fitted: FittedStrategy | None = None, **kw: object) -> BacktestResult:
        fs = fitted or self.fit(genome, fit_window)
        sig = self.signal(fs)
        if count:
            self.evaluations += 1
        return run_backtest(self.market, sig, genome.direction, genome.hold, genome.stop, genome.take,
                            self.costs, eval_window, trail=genome.trail, **kw)  # type: ignore[arg-type]

    def with_costs(self, costs: CostModel) -> EvalContext:
        return EvalContext(self.market, self.prims, self.exprs, costs, self.regimes, self.cache, self.evaluations)
