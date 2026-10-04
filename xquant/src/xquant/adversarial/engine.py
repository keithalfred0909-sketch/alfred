"""ADVERSARIAL ENGINE: tries to destroy every candidate strategy before it can be called robust.

Each attack answers one question and is classified:
  reject  - failing it means the edge is not real or not tradeable           -> REJECTED
  overfit - failing it means the result depends on the exact configuration    -> OVERFIT
  warn    - informative; reported but not decisive

All attacks run on TRAIN+VALIDATION with thresholds fitted on TRAIN. TEST and FINAL are untouched here.
Negative results are kept and reported, never hidden.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from xquant.config import RobustnessSpec
from xquant.strategy.evaluator import EvalContext
from xquant.strategy.genome import Genome
from xquant.validation import robustness as rb
from xquant.validation.overfit import deflated_sharpe_report
from xquant.validation.splits import DataSplits, SplitGuard

# Bump whenever the attack battery changes meaningfully. Stored with every dossier; a strategy examined with
# an older battery is re-examined instead of reusing its verdict (a corrected test is a new scientific reason).
# v2: entry displacement uses delays (+1, +2) only.
ATTACK_SUITE_VERSION = 2
EQUITY_POINTS = 400


@dataclass
class Attack:
    name: str
    question: str
    kind: str  # reject | overfit | warn
    passed: bool | None
    value: Any
    threshold: Any

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Dossier:
    genome: Genome
    strategy_id: str = ""
    train: dict[str, Any] = field(default_factory=dict)
    validation: dict[str, Any] = field(default_factory=dict)
    test: dict[str, Any] = field(default_factory=dict)
    final: dict[str, Any] = field(default_factory=dict)
    walk_forward: dict[str, Any] = field(default_factory=dict)
    monte_carlo: dict[str, Any] = field(default_factory=dict)
    robustness: dict[str, Any] = field(default_factory=dict)
    overfit: dict[str, Any] = field(default_factory=dict)
    attacks: list[Attack] = field(default_factory=list)
    status: str = "CANDIDATE"
    reasons: list[str] = field(default_factory=list)
    score: float = float("nan")
    equity: dict[str, list[Any]] = field(default_factory=dict)

    @property
    def passed_attacks(self) -> int:
        return sum(a.passed is True for a in self.attacks)

    @property
    def decisive_attacks(self) -> int:
        return sum(a.passed is not None and a.kind != "warn" for a in self.attacks)

    def to_dict(self) -> dict[str, Any]:
        def clean(x: Any) -> Any:
            if isinstance(x, float):
                return x if math.isfinite(x) else None
            if isinstance(x, dict):
                return {str(k): clean(v) for k, v in x.items()}
            if isinstance(x, list | tuple):
                return [clean(v) for v in x]
            if isinstance(x, np.floating | np.integer):
                return clean(x.item())
            if isinstance(x, np.bool_):
                return bool(x)
            if isinstance(x, pd.Series):
                return None
            return x
        return clean({"strategy_id": self.strategy_id, "attack_suite_version": ATTACK_SUITE_VERSION,
                      "genome": self.genome.to_dict(),
                      "description": self.genome.describe(), "complexity": self.genome.complexity,
                      "status": self.status, "reasons": self.reasons, "score": self.score,
                      "train": self.train, "validation": self.validation, "test": self.test, "final": self.final,
                      "walk_forward": {k: v for k, v in self.walk_forward.items() if k != "returns"},
                      "monte_carlo": self.monte_carlo, "robustness": self.robustness, "overfit": self.overfit,
                      "attacks": [a.to_dict() for a in self.attacks], "equity": self.equity})


class AdversarialEngine:
    def __init__(self, ctx: EvalContext, splits: DataSplits, guard: SplitGuard, spec: RobustnessSpec,
                 rebuild: Callable[[pd.DataFrame], EvalContext], bars: pd.DataFrame, tz: str,
                 min_trades: int, rng: np.random.Generator) -> None:
        self.ctx, self.splits, self.guard, self.spec = ctx, splits, guard, spec
        self.rebuild, self.bars, self.tz = rebuild, bars, tz
        self.min_trades, self.rng = min_trades, rng
        self.train = splits.slice("train")
        self.val = splits.slice("validation")
        self.combined = slice(0, self.val.stop)

    def examine(self, g: Genome, n_trials: int, var_sr_annual: float, pbo: dict[str, Any] | None) -> Dossier:
        d = Dossier(genome=g)
        sp = self.spec
        ctx, tr, va, cb = self.ctx, self.train, self.val, self.combined
        A = d.attacks.append

        tr_res = ctx.backtest(g, tr, tr)
        d.train = dict(tr_res.metrics.to_dict())
        self.guard.request("validation", "evaluate", f"adversarial:{g.signature}")
        va_res = ctx.backtest(g, tr, va)
        d.validation = dict[str, Any](va_res.metrics.to_dict())
        d.validation["sharpe_ci"] = rb.bootstrap_sharpe_ci(va_res.returns.to_numpy(), ctx.market.ppy, 300, self.rng)
        vm = va_res.metrics
        A(Attack("out_of_sample_validation", "Does it work out of sample (VALIDATION, thresholds from TRAIN)?",
                 "reject", bool(vm.sharpe > 0 and vm.total_return > 0 and vm.profit_factor > 1 and vm.trades >= 5),
                 {"sharpe": vm.sharpe, "pf": vm.profit_factor, "trades": vm.trades}, "SR>0, PF>1, >=5 trades"))

        cb_res = ctx.backtest(g, tr, cb)
        cm = cb_res.metrics
        A(Attack("enough_trades", "Is the sample of trades large enough?", "reject", bool(cm.trades >= self.min_trades),
                 cm.trades, f">= {self.min_trades}"))
        re = rb.random_entry_test(ctx, g, cb_res, cb, sp.random_entry_reps, self.rng)
        d.monte_carlo["random_entry"] = re
        A(Attack("beats_random_entries", "Does its timing beat random entries with the same exits and costs?",
                 "reject", None if re.get("status") != "OK" else bool(re["p_value"] < sp.max_random_entry_pvalue),
                 re.get("p_value"), f"p < {sp.max_random_entry_pvalue}"))

        wf = rb.walk_forward(ctx, g, cb, sp.wf_windows, "rolling")
        wfe = rb.walk_forward(ctx, g, cb, sp.wf_windows, "expanding")
        d.walk_forward = {"rolling": {k: v for k, v in wf.items() if k != "returns"},
                          "expanding": {k: v for k, v in wfe.items() if k != "returns"}}
        ok_wf = wf.get("status") == "OK"
        A(Attack("walk_forward", "Does it survive rolling walk-forward re-fitting?", "reject",
                 None if not ok_wf else bool(wf["oos_sharpe"] > 0 and wf["positive_windows"] >= 0.5),
                 {"oos_sharpe": wf.get("oos_sharpe"), "positive_windows": wf.get("positive_windows")},
                 "OOS SR>0 and >=50% windows positive"))

        pp = rb.parameter_perturbation(ctx, g, tr, cb, sp.param_perturbation)
        d.robustness["parameters"] = pp
        A(Attack("parameter_perturbation", f"Does it survive +/-{sp.param_perturbation:.0%} parameter changes?", "overfit",
                 None if pp.get("status") != "OK" else bool(pp["profitable_share"] >= sp.min_param_stability),
                 pp.get("profitable_share"), f">= {sp.min_param_stability}"))

        cs = rb.cost_stress(ctx, g, tr, cb, sp.cost_stress_multipliers)
        d.robustness["costs"] = cs
        x2 = cs.get("x2", {})
        A(Attack("spread_slippage_x2", "Does it survive doubled spread, commission and slippage?", "reject",
                 bool(x2.get("sharpe", -1) > 0 and x2.get("total_return", -1) > 0), x2.get("sharpe"), "SR>0 at 2x costs"))
        x3 = cs.get("x3", {})
        A(Attack("spread_slippage_x3", "Does it survive tripled costs?", "warn",
                 bool(x3.get("sharpe", -1) > 0), x3.get("sharpe"), "SR>0 at 3x costs"))
        A(Attack("latency_plus1", "Does it survive one extra bar of latency?", "reject",
                 bool(cs["latency_plus1"]["sharpe"] > 0), cs["latency_plus1"]["sharpe"], "SR>0"))
        sh = [cs["entry_shift_+1"]["sharpe"], cs["entry_shift_+2"]["sharpe"]]
        A(Attack("entry_displacement", "Does it survive entries delayed by 1 and 2 bars?", "reject",
                 bool(min(sh) > 0), sh, "SR>0 for both delays"))

        rx = rb.randomized_execution(ctx, g, tr, cb, 50, self.rng)
        d.robustness["randomized_execution"] = rx
        A(Attack("randomized_execution", "Does it survive random delays and 10% skipped trades?", "reject",
                 bool(rx["positive_share"] >= 0.6), rx["positive_share"], ">= 0.6 of runs SR>0"))

        bd = rb.breakdowns(cb_res, ctx.regimes, self.tz)
        d.robustness["breakdowns"] = bd
        A(Attack("other_years", "Does it work across years, not only in some?", "reject",
                 bool(bd["profitable_year_share"] >= sp.min_profitable_year_share), bd["profitable_year_share"],
                 f">= {sp.min_profitable_year_share}"))
        top = bd.get("top5pct_trade_share", float("inf"))
        A(Attack("few_trades_dependence", "Does profit depend on a handful of trades?", "reject",
                 bool(top <= sp.max_top_trade_share), top, f"top 5% trades <= {sp.max_top_trade_share:.0%} of profit"))
        A(Attack("single_event_dependence", "Is it still profitable without its best month?", "reject",
                 bool(bd.get("without_best_month", -1) > 0), bd.get("without_best_month"), "> 0"))
        if g.regime is None and "max_regime_profit_share" in bd:
            A(Attack("other_regimes", "Does it work in more than one market regime?", "reject",
                     bool(bd["max_regime_profit_share"] <= 0.85), bd["max_regime_profit_share"], "<= 85% from one regime"))
        if not any(c.feature in ("dow", "hour") for c in g.conditions):
            A(Attack("schedule_dependence", "Does it depend on one weekday/hour?", "reject",
                     bool(bd.get("max_weekday_profit_share", 1.0) <= 0.6), bd.get("max_weekday_profit_share"), "<= 60%"))

        dp = rb.data_perturbation(self.rebuild, self.bars, g, tr, cb, sp.noise_vol_fraction, 8, self.rng)
        d.robustness["data_noise"] = dp
        A(Attack("data_perturbation", "Does it survive small noise added to prices?", "overfit",
                 bool(dp["positive_share"] >= 0.6), dp["positive_share"], ">= 0.6 of runs SR>0"))
        tf = rb.timeframe_perturbation(self.rebuild, self.bars, g, tr, cb, self.min_trades)
        d.robustness["timeframe"] = tf
        okp = [v["sharpe"] > 0 for v in tf.values() if v["status"] == "OK"]
        A(Attack("timeframe_perturbation", "Does the effect persist at a coarser sampling (2x bar)?", "warn",
                 None if not okp else bool(all(okp)), {k: v["sharpe"] for k, v in tf.items()}, "SR>0 both phases"))

        mc = rb.trade_bootstrap(cb_res.trade_net, sp.mc_reps, self.rng)
        d.monte_carlo["trade_bootstrap"] = mc
        A(Attack("monte_carlo_loss_probability", "Under trade-order bootstrap, is a loss unlikely?", "reject",
                 None if mc.get("status") != "OK" else bool(mc["p_loss"] <= 0.2), mc.get("p_loss"), "<= 0.2"))

        ds = deflated_sharpe_report(tr_res.returns.to_numpy(), n_trials, var_sr_annual, ctx.market.ppy)
        d.overfit["deflated_sharpe"] = ds
        A(Attack("deflated_sharpe", f"Is the train Sharpe significant after {n_trials} trials?", "overfit",
                 bool(ds["dsr"] >= sp.min_deflated_sharpe_prob), ds["dsr"], f">= {sp.min_deflated_sharpe_prob}"))
        if pbo and pbo.get("status") == "OK":
            d.overfit["pbo"] = pbo
            A(Attack("probability_backtest_overfitting", "Is the search process itself overfitting (CSCV PBO)?",
                     "overfit", bool(pbo["pbo"] <= sp.max_pbo), pbo["pbo"], f"<= {sp.max_pbo}"))
        d.overfit["is_oos_degradation"] = (vm.sharpe / tr_res.metrics.sharpe) if tr_res.metrics.sharpe > 0 else None

        self._verdict(d)
        eq = np.cumsum(cb_res.returns.to_numpy())
        step = max(1, len(eq) // EQUITY_POINTS)  # enough to draw the curve; keeps memory/report small
        d.equity["combined"] = [round(float(x), 6) for x in eq[::step]]
        d.equity["dates"] = [str(t.date()) for t in cb_res.returns.index[::step]]
        return d

    @staticmethod
    def _verdict(d: Dossier) -> None:
        rej = [a for a in d.attacks if a.kind == "reject" and a.passed is False]
        ovf = [a for a in d.attacks if a.kind == "overfit" and a.passed is False]
        d.reasons = [f"{a.name}: {a.question} -> value {a.value!r} vs {a.threshold}" for a in rej + ovf]
        if rej:
            d.status = "REJECTED"
        elif ovf:
            d.status = "OVERFIT"
        else:
            d.status = "PASSED_SELECTION"


def score(d: Dossier, round_trip: float) -> float:
    """Composite ranking score. Robustness and out-of-sample evidence dominate; returns matter last."""
    v = d.validation
    wf = d.walk_forward.get("rolling", {})
    pp = d.robustness.get("parameters", {})
    decisive = max(d.decisive_attacks, 1)
    pass_rate = sum(a.passed is True and a.kind != "warn" for a in d.attacks) / decisive
    pf = v.get("profit_factor") or 0.0
    pf = 5.0 if not math.isfinite(pf) else pf
    s = (1.5 * pass_rate + 1.0 * (v.get("sharpe") or 0.0) + 0.5 * (wf.get("oos_sharpe") or 0.0)
         + 0.25 * math.tanh(pf - 1) + 0.25 * (v.get("stability") or 0.0) + 0.1 * (v.get("sortino") or 0.0)
         + 0.25 * math.tanh((v.get("expectancy") or 0.0) / max(round_trip, 1e-9))
         - 0.1 * d.genome.complexity - 1.0 * (v.get("max_drawdown") or 0.0)
         - 0.5 * (1 - (pp.get("profitable_share") or 0.0)))
    return float(s)
