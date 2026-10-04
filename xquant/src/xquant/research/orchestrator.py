"""AUTONOMOUS RESEARCH MODE.

The orchestrator owns a research cycle for one asset:

    data -> market behaviour -> macro -> news -> features -> hypotheses
         -> evolution lines (repeated, each run = experiment) -> adversarial examination
         -> TEST (once per surviving finalist) -> ranking -> FINAL out-of-sample (once, #1 only)
         -> scenario analysis -> verdict -> report

Research lines stop on their own when: no improvement, repeated failure, insufficient evidence,
overfitting detected, or data quality insufficient. The whole cycle stops when every line has stopped
or a budget (experiments, compute time, strategies) is exhausted. No step waits for user input.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np
import pandas as pd

from xquant.adversarial.engine import ATTACK_SUITE_VERSION, AdversarialEngine, Dossier, score
from xquant.backtest.engine import MarketArrays
from xquant.config import XQuantConfig
from xquant.data.engine import DataEngine, MarketDataset
from xquant.errors import DataQualityError, DataUnavailableError, InsufficientDataError, XQuantError
from xquant.evolution.engine import EvolutionEngine
from xquant.features.discovery import FeatureDiscovery, FeaturePool
from xquant.features.library import CATEGORICAL, assert_causal, build_primitives, evaluate
from xquant.findings import Finding
from xquant.hypothesis.engine import Hypothesis, HypothesisEngine
from xquant.logging_utils import get_logger
from xquant.macro.engine import MacroEngine
from xquant.market.behavior import MarketBehaviorEngine, periods_per_year
from xquant.market.regimes import RegimeModel
from xquant.memory.store import ResearchMemory
from xquant.news.engine import NewsEngine
from xquant.probability.engine import ScenarioReport, scenario_analysis
from xquant.strategy.evaluator import EvalContext
from xquant.strategy.genome import Genome, genome_from_hypothesis
from xquant.validation.overfit import deflated_sharpe_report, pbo_cscv
from xquant.validation.splits import DataSplits, SplitGuard, make_splits

log = get_logger("research")

LINES = ["hypothesis_seeded", "open_exploration", "regime_conditioned", "macro_conditioned"]


@dataclass
class LineState:
    name: str
    status: str = "ACTIVE"
    experiments: int = 0
    failures: int = 0
    best_score: float = -math.inf
    overfit: int = 0
    examined: int = 0
    stop_reason: str = ""


@dataclass
class ResearchOutcome:
    run_id: str
    asset: str
    verdict: str
    verdict_detail: str
    dataset: dict[str, Any] = field(default_factory=dict)
    splits: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    features: dict[str, Any] = field(default_factory=dict)
    hypotheses: dict[str, Any] = field(default_factory=dict)
    lines: list[dict[str, Any]] = field(default_factory=list)
    dossiers: list[dict[str, Any]] = field(default_factory=list)
    ranking: list[dict[str, Any]] = field(default_factory=list)
    failure_summary: dict[str, int] = field(default_factory=dict)
    scenario: dict[str, Any] = field(default_factory=dict)
    budget: dict[str, Any] = field(default_factory=dict)
    trials: dict[str, Any] = field(default_factory=dict)
    split_access: list[dict[str, str]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0


class ResearchOrchestrator:
    def __init__(self, cfg: XQuantConfig, offline: bool = False, memory: ResearchMemory | None = None,
                 dataset: MarketDataset | None = None, progress: Callable[[str], None] | None = None) -> None:
        self.cfg = cfg
        self.offline = offline
        self.memory = memory or ResearchMemory(cfg.research.memory_path)
        self._dataset = dataset
        self.rng = np.random.default_rng(cfg.research.seed)
        self.budget = cfg.budget
        self.guard = SplitGuard()
        self.progress_cb = progress
        self.t0 = time.time()
        self.deadline = self.t0 + self.budget.max_compute_minutes * 60
        self.experiments = 0
        self.examined = 0
        self.asset = cfg.asset.symbol
        self.run_id = ""
        self.dv = ""
        self.cfp = cfg.fingerprint()

    # ---- bookkeeping -------------------------------------------------------------------------------
    def _say(self, msg: str, level: str = "INFO") -> None:
        log.log(20 if level == "INFO" else 30, msg)
        if self.run_id:
            self.memory.log(self.run_id, msg, level)
        if self.progress_cb:
            self.progress_cb(msg)

    def _progress(self, **kw: Any) -> None:
        kw.update(experiments=self.experiments, examined=self.examined,
                  elapsed_min=round((time.time() - self.t0) / 60, 2))
        self.memory.update_run(self.run_id, progress=kw)

    def _experiment(self, kind: str, line: str, params: dict[str, Any], metrics: dict[str, Any], conclusion: str,
                    status: str, t_start: float) -> str:
        self.experiments += 1
        return self.memory.record_experiment(self.run_id, kind, line, self.asset, self.dv, self.cfp,
                                             self.cfg.research.seed, params, metrics, conclusion, status,
                                             time.time() - t_start)

    def _budget_left(self) -> str | None:
        if self.experiments >= self.budget.max_experiments:
            return f"max_experiments ({self.budget.max_experiments}) reached"
        if time.time() > self.deadline:
            return f"max_compute_minutes ({self.budget.max_compute_minutes}) reached"
        if self.examined >= self.budget.max_strategies:
            return f"max_strategies ({self.budget.max_strategies}) examined"
        return None

    # ---- context ---------------------------------------------------------------------------------
    def _build_context(self, bars: pd.DataFrame, exog: pd.DataFrame, exprs: dict[str, Any] | None,
                       regime_model: RegimeModel | None, ppy: float) -> EvalContext:
        prims = build_primitives(bars, exog.reindex(bars.index) if not exog.empty else None, self.cfg.asset.timezone)
        regimes = regime_model.predict(bars["close"]) if regime_model else None
        return EvalContext(MarketArrays.from_bars(bars, ppy), prims, exprs or {}, self.cfg.asset.costs, regimes)

    # ---- main ------------------------------------------------------------------------------------
    def run(self) -> ResearchOutcome:
        """Run a full cycle. Unexpected failures mark the run FAILED in memory (with the error) and re-raise."""
        try:
            return self._run()
        except Exception as exc:
            if self.run_id:
                self.memory.update_run(self.run_id, status="FAILED", verdict="FAILED",
                                       finished_at=pd.Timestamp.now(tz="UTC").isoformat(),
                                       summary={"detail": f"{type(exc).__name__}: {exc}"})
                self.memory.log(self.run_id, f"run failed: {type(exc).__name__}: {exc}", "ERROR")
            raise

    def _run(self) -> ResearchOutcome:
        cfg = self.cfg
        out = ResearchOutcome(run_id="", asset=self.asset, verdict="", verdict_detail="")
        # 1. DATA
        t = time.time()
        try:
            ds = self._dataset or DataEngine(cfg.asset, offline=self.offline).load()
        except (DataUnavailableError, DataQualityError) as exc:
            self.run_id = self.memory.start_run(self.asset, cfg.research.mode, "n/a", self.cfp, cfg.research.seed)
            self._experiment("data", "data", {}, {}, f"data unavailable or failed validation: {exc}", "FAILED", t)
            return self._finish(out, "INSUFFICIENT DATA", f"Data could not be loaded or validated: {exc}")
        self.dv = ds.version
        self.run_id = self.memory.start_run(self.asset, cfg.research.mode, self.dv, self.cfp, cfg.research.seed)
        out.run_id = self.run_id
        out.dataset = {**ds.summary(), "quality_report": ds.quality.to_dict(), "notes": ds.meta.notes,
                       "exogenous_meta": ds.exog_meta,
                       "exog_latest": {c: {"value": float(ds.exog[c].dropna().iloc[-1]),
                                           "as_of_bar": str(ds.exog[c].dropna().index[-1].date())}
                                       for c in ds.exog.columns if ds.exog[c].notna().any()},
                       "last_close": float(ds.bars["close"].iloc[-1])}
        self._say(f"{self.run_id}: research started on {self.asset} ({cfg.research.mode}); dataset {self.dv}")
        try:
            splits = make_splits(pd.DatetimeIndex(ds.bars.index), cfg.asset.splits)
        except InsufficientDataError as exc:
            return self._finish(out, "INSUFFICIENT DATA", str(exc))
        out.splits = {k: {"span": splits.span(k), "bars": v} for k, v in splits.sizes().items()}  # type: ignore[arg-type]
        self._experiment("data", "data", {"source": ds.meta.source}, ds.summary(),
                         f"quality {ds.quality.verdict}; {ds.meta.n_rows} bars", "OK", t)
        self._progress(phase="market_behavior")

        # 2-4. EXPLORATORY ENGINES
        ppy = periods_per_year(pd.DatetimeIndex(ds.bars.index))
        mb = MarketBehaviorEngine(ds, splits, cfg.stats.horizons, seed=cfg.research.seed, tz=cfg.asset.timezone)
        findings = self._run_findings("market_behavior", lambda: mb.run(cfg.stats.fdr_alpha))
        regime_model = mb.regimes
        regimes = regime_model.predict(ds.bars["close"]) if regime_model else None
        self._progress(phase="macro")
        findings += self._run_findings("macro", lambda: MacroEngine(ds, splits, regimes).run(cfg.stats.fdr_alpha))
        findings += self._run_findings("news", lambda: NewsEngine(ds, splits, regimes=regimes).run(cfg.stats.fdr_alpha))
        out.findings = [f.to_dict() for f in findings]
        if self._budget_left():
            return self._finish(out, "NO EDGE FOUND", f"budget exhausted before strategy research: {self._budget_left()}")

        # 5. FEATURES
        self._progress(phase="feature_discovery")
        t = time.time()
        ctx = self._build_context(ds.bars, ds.exog, None, regime_model, ppy)
        self._lookahead_audit(ds, ctx)
        fd = FeatureDiscovery(ctx.prims, ds.bars["close"], splits.slice("train"), cfg.asset.splits.embargo_bars,
                              cfg.stats.horizons, cfg.research.seed, self.budget.max_features,
                              min(self.budget.max_complexity, 4), cfg.stats.fdr_alpha)
        pool = fd.run()
        ctx.exprs = pool.exprs
        ctx.cache = fd.cache
        out.features = {"candidates": len(pool.exprs), "tests": len(pool.scores), "confirmed": pool.confirmed[:50],
                        "status_counts": pd.Series([s.status for s in pool.scores]).value_counts().to_dict()
                        if pool.scores else {},
                        "top": [s.to_dict() for s in sorted([s for s in pool.scores if s.status == "CONFIRMED"],
                                                            key=lambda s: -abs(s.ic_conf))[:15]]}
        self._experiment("feature_discovery", "features", {"max_features": self.budget.max_features},
                         {"confirmed": len(pool.confirmed), "tests": len(pool.scores)},
                         f"{len(pool.confirmed)} features confirmed on inner holdout", "OK", t)

        # 6. HYPOTHESES
        self._progress(phase="hypotheses")
        validated = self._hypotheses(ctx, pool, ds, splits, regimes, out)

        # 7. EVOLUTION LINES + ADVERSARIAL
        rebuild = lambda bars: self._build_context(bars, ds.exog, pool.exprs, regime_model,  # noqa: E731
                                                   ppy * len(bars) / len(ds.bars))
        adv = AdversarialEngine(ctx, splits, self.guard, cfg.robustness, rebuild, ds.bars, cfg.asset.timezone,
                                cfg.stats.min_trades, np.random.default_rng(cfg.research.seed + 1))
        dossiers = self._evolution_lines(ctx, pool, validated, splits, adv, regime_model, out)

        # 8. TEST, RANKING, FINAL
        self._progress(phase="final_evaluation")
        self._final_stage(ctx, splits, dossiers, out)
        out.trials = dict(zip(["n_trials", "sr_var_per_period"], self.memory.trials(self.asset, self.dv), strict=True))

        # 9. SCENARIOS
        out.scenario = self._scenario(ds, ctx, pool, validated, regimes).to_dict()
        return self._finish(out, *self._verdict(out))

    # ---- stages ------------------------------------------------------------------------------------
    def _run_findings(self, line: str, fn: Callable[[], list[Finding]]) -> list[Finding]:
        t = time.time()
        try:
            fs = fn()
        except XQuantError as exc:
            self._say(f"{line}: stopped ({exc})", "WARNING")
            self._experiment(line, line, {}, {}, f"stopped: {exc}", "FAILED", t)
            return [Finding.insufficient(line, "engine", line, str(exc))]
        disc = [f for f in fs if f.status == "DISCOVERY"]
        eid = self._experiment(line, line, {}, {"findings": len(fs), "discoveries": len(disc),
                                                "insufficient": sum(f.status == "INSUFFICIENT DATA" for f in fs)},
                               f"{len(disc)} replicated discoveries: {[f.name for f in disc]}", "OK", t)
        self.memory.record_findings(self.run_id, eid, self.asset, self.dv, [f.to_dict() for f in fs])
        self._say(f"{line}: {len(fs)} findings, {len(disc)} replicated discoveries")
        return fs

    def _lookahead_audit(self, ds: MarketDataset, ctx: EvalContext) -> None:
        """Run the truncation test on a sample of primitives on the real dataset (cheap insurance)."""
        n = len(ds.bars)
        cuts = sorted({int(n * 0.5), int(n * 0.8), n - 1})
        names = list(ctx.prims)[:: max(1, len(ctx.prims) // 12)]
        tz = self.cfg.asset.timezone

        def prim_fn(nm: str) -> Callable[[pd.DataFrame], pd.Series]:
            return lambda b: build_primitives(b, ds.exog.loc[b.index] if not ds.exog.empty else None, tz)[nm]
        for name in names:
            assert_causal(prim_fn(name), ds.bars, cuts, name)
        self._say(f"look-ahead audit passed on {len(names)} primitives x {len(cuts)} truncation points")

    def _hypotheses(self, ctx: EvalContext, pool: FeaturePool, ds: MarketDataset, splits: DataSplits,
                    regimes: pd.Series | None, out: ResearchOutcome) -> list[Hypothesis]:
        t = time.time()
        disc, conf = pool.inner_split
        he = HypothesisEngine(ctx.prims, pool.exprs, ds.bars["close"], disc, conf, self.cfg.stats.horizons,
                              self.cfg.stats.quantiles, self.cfg.stats.fdr_alpha, self.cfg.stats.min_samples,
                              self.cfg.stats.min_effect_size, regimes, ctx.cache,
                              period=f"{ds.bars.index[disc.start].date()} to {ds.bars.index[disc.stop - 1].date()}")
        feats = pool.hypothesis_features(self.budget.max_features)
        hyps = he.generate(feats, with_regimes=False)[: self.budget.max_hypotheses]
        known = self.memory.known_hypotheses(self.asset, self.dv)
        new = [h for h in hyps if h.signature not in known]
        reused = len(hyps) - len(new)
        if reused:
            self._say(f"hypotheses: {reused} already tested on this dataset version -> DO NOT REDISCOVER (reused)")
        he.test(new)
        eid = self._experiment("hypotheses", "hypotheses", {"features": len(feats), "generated": len(hyps)},
                               {"new": len(new), "reused": reused,
                                "validated": sum(h.status == "VALIDATION" for h in new)},
                               "hypothesis batch tested with BH-FDR and inner-holdout confirmation", "OK", t)
        ids = self.memory.record_hypotheses(self.asset, self.dv, eid, [h.to_dict() for h in new])
        for h, i in zip(new, ids, strict=True):
            h.id = i
        validated = [h for h in new if h.status == "VALIDATION"]
        for k in known.values():
            if k["status"] == "VALIDATION":
                d = k["data"]
                h = Hypothesis(d["feature"], d["side"], d["q"], d["horizon"], d.get("regime"), d["threshold"] or float("nan"),
                               id=k["id"], effect=d["effect"] or 0.0, status="VALIDATION")
                if h.feature in pool.exprs:
                    validated.append(h)
        validated.sort(key=lambda h: -abs(h.effect_size) if math.isfinite(h.effect_size) else 0)
        all_status = [h.status for h in new] + [k["status"] for s_, k in known.items()
                                                 if s_ in {h.signature for h in hyps}]
        counts = pd.Series(all_status).value_counts().to_dict() if all_status else {}
        out.hypotheses = {"generated": len(hyps), "new": len(new), "reused": reused, "status_counts": counts,
                          "validated": [h.to_dict() for h in validated[:25]],
                          "top_rejected_or_overfit": [h.to_dict() for h in sorted(
                              [h for h in new if h.status == "OVERFIT"], key=lambda h: h.p_value)[:10]]}
        self._say(f"hypotheses: {len(new)} new tested, {reused} reused, {len(validated)} in VALIDATION state, statuses {counts}")
        return validated

    def _line_setup(self, line: str, pool: FeaturePool, validated: list[Hypothesis],
                    regime_model: RegimeModel | None) -> tuple[list[str], list[Genome], int] | str:
        feats = pool.hypothesis_features(self.budget.max_features)
        n_reg = regime_model.k if regime_model else 0
        if line == "hypothesis_seeded":
            if not validated:
                return "evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation"
            seeds = [genome_from_hypothesis(h) for h in validated]
            feats = list(dict.fromkeys([h.feature for h in validated] + feats))
            return feats, seeds, 0
        if line == "open_exploration":
            return feats, [], 0
        if line == "regime_conditioned":
            if not n_reg:
                return "evidence insufficient: no regime model"
            return feats, [], n_reg
        if line == "macro_conditioned":
            mf = [f for f in feats if f.startswith("x_")]
            if not mf:
                return "data insufficient: no macro/cross-asset features available"
            return mf + [f for f in feats if not f.startswith("x_")][:20], [], 0
        return "unknown line"

    def _evolution_lines(self, ctx: EvalContext, pool: FeaturePool, validated: list[Hypothesis], splits: DataSplits,
                         adv: AdversarialEngine, regime_model: RegimeModel | None, out: ResearchOutcome) -> list[Dossier]:
        states = {name: LineState(name) for name in LINES}
        categorical = {}
        train = splits.slice("train")
        for f in CATEGORICAL:
            if f in ctx.prims:
                vals = ctx.prims[f].iloc[train].dropna().unique()
                categorical[f] = sorted(float(v) for v in vals)
        dossiers: list[Dossier] = []
        round_trip = 2 * (self.cfg.asset.costs.spread_bps / 2 + self.cfg.asset.costs.commission_bps
                          + self.cfg.asset.costs.slippage_bps) * 1e-4
        run_seed = 0
        while any(s.status == "ACTIVE" for s in states.values()):
            for name, st in states.items():
                if st.status != "ACTIVE":
                    continue
                why = self._budget_left()
                if why:
                    for s in states.values():
                        if s.status == "ACTIVE":
                            s.status, s.stop_reason = "STOPPED", f"budget: {why}"
                    break
                setup = self._line_setup(name, pool, validated, regime_model)
                if isinstance(setup, str):
                    st.status, st.stop_reason = "STOPPED", setup
                    self._say(f"line {name}: stopped ({setup})")
                    continue
                feats, seeds, n_reg = setup
                feats = [f for f in feats if f in pool.exprs]
                run_seed += 1
                self._progress(phase="evolution", line=name, line_run=st.experiments + 1)
                t = time.time()
                rng = np.random.default_rng(self.cfg.research.seed * 1000 + run_seed)
                eng = EvolutionEngine(ctx, train, feats, {k: v for k, v in categorical.items() if k in feats},
                                      seeds, rng, self.budget.population, self.budget.max_generations,
                                      self.budget.patience, self.budget.max_complexity, self.cfg.stats.min_trades,
                                      n_regimes=n_reg, deadline=self.deadline)
                if name == "regime_conditioned":
                    eng.seeds = [replace(eng._random(), regime=int(rng.integers(n_reg))) for _ in range(eng.pop_size // 2)]
                if name == "macro_conditioned":
                    mf = [f for f in feats if f.startswith("x_")]
                    eng.seeds = [self._macro_seed(eng, rng, mf) for _ in range(eng.pop_size // 2)]
                res = eng.run()
                n_trials, _ = self.memory.add_trials(self.asset, self.dv, res.sr_trials)
                _, var = self.memory.trials(self.asset, self.dv)
                pbo = self._pbo(ctx, res, train)
                examined_here: list[Dossier] = []
                skipped = 0
                for ind in res.elite:
                    if len(examined_here) >= 5 or self._budget_left():
                        break
                    g = ind.genome
                    prior = self.memory.known_strategy(g.signature, self.asset, self.dv)
                    if prior and prior["dossier"].get("attack_suite_version", 1) == ATTACK_SUITE_VERSION:
                        # DO NOT REDISCOVER: same data, same battery -> reuse the stored verdict
                        skipped += 1
                        continue
                    d = adv.examine(g, n_trials, var, pbo)
                    d.score = score(d, round_trip)
                    self.examined += 1
                    examined_here.append(d)
                if skipped:
                    self._say(f"line {name}: {skipped} elite genome(s) already examined on this dataset -> skipped")
                eid = self._experiment(
                    "evolution", name, {"seed": int(self.cfg.research.seed * 1000 + run_seed), "features": len(feats),
                                        "population": self.budget.population, "generations": res.generations},
                    {"evaluated": res.evaluations, "best_fitness": res.best_history[-1] if res.best_history else None,
                     "elite": len(res.elite), "pbo": pbo.get("pbo"),
                     "examined": [(d.genome.signature, d.status) for d in examined_here]},
                    f"{res.stop_reason}; examined {len(examined_here)}: "
                    + ", ".join(f"{d.status}" for d in examined_here), "OK", t)
                for d in examined_here:
                    payload = d.to_dict()
                    payload["genome_signature"] = d.genome.signature
                    d.strategy_id = self.memory.record_strategy(self.run_id, eid, self.asset, self.dv, payload)
                    dossiers.append(d)
                st.experiments += 1
                st.examined += len(examined_here)
                st.overfit += sum(d.status == "OVERFIT" for d in examined_here)
                passed = [d for d in examined_here if d.status == "PASSED_SELECTION"]
                best_now = max([d.score for d in examined_here], default=-math.inf)
                improved = best_now > st.best_score + 0.05
                if passed and improved:
                    st.failures = 0
                else:
                    st.failures += 1
                st.best_score = max(st.best_score, best_now)
                self._say(f"line {name} run {st.experiments}: {res.evaluations} genomes, elite {len(res.elite)}, "
                          f"examined {len(examined_here)} -> {[d.status for d in examined_here]}")
                if not res.elite:
                    st.failures = max(st.failures, self.budget.max_line_failures)
                    st.status, st.stop_reason = "STOPPED", "repeated failure: no genome with positive fitness on TRAIN"
                elif st.examined >= 6 and st.overfit / st.examined > 0.8:
                    st.status, st.stop_reason = "STOPPED", "overfitting detected in >80% of examined candidates"
                elif st.failures >= self.budget.max_line_failures:
                    st.status, st.stop_reason = "STOPPED", f"no improvement / repeated failure ({st.failures} runs)"
                self.memory.set_line(self.run_id, name, st.status, st.experiments, st.failures, st.stop_reason,
                                     st.best_score if math.isfinite(st.best_score) else None)
        out.lines = [s.__dict__ | {"best_score": s.best_score if math.isfinite(s.best_score) else None}
                     for s in states.values()]
        for s in states.values():
            self.memory.set_line(self.run_id, s.name, s.status, s.experiments, s.failures, s.stop_reason,
                                 s.best_score if math.isfinite(s.best_score) else None)
        return dossiers

    @staticmethod
    def _macro_seed(eng: EvolutionEngine, rng: np.random.Generator, macro_feats: list[str]) -> Genome:
        from xquant.strategy.genome import TAILS, Condition
        g = eng._random()
        c = Condition(str(rng.choice(macro_feats)), str(rng.choice(["low", "high"])), float(rng.choice(TAILS)))
        return replace(g, conditions=(c,) + tuple(x for x in g.conditions if x.feature != c.feature)[:1], origin="macro_seed")

    def _pbo(self, ctx: EvalContext, res: Any, train: slice) -> dict[str, Any]:
        cands = [i for i in res.population if i.fitness > -5][:30]
        if len(cands) < 4:
            return {"status": "INSUFFICIENT DATA"}
        mat = np.column_stack([ctx.backtest(i.genome, train, train, count=False).returns.to_numpy() for i in cands])
        return pbo_cscv(mat)

    def _final_stage(self, ctx: EvalContext, splits: DataSplits, dossiers: list[Dossier], out: ResearchOutcome) -> None:
        self._refresh_deflated_sharpe(ctx, splits, dossiers)
        finalists = sorted([d for d in dossiers if d.status == "PASSED_SELECTION"], key=lambda d: -d.score)
        pre_test = slice(0, splits.bounds["validation"][1])
        test = splits.slice("test")
        if finalists:
            self._say(f"TEST: opening TEST split for {len(finalists)} finalist(s); optimisation is now frozen")
        for d in finalists:
            self.guard.request("test", "evaluate", f"final_stage:{d.genome.signature}")
            m = ctx.backtest(d.genome, pre_test, test, count=False).metrics
            d.test = m.to_dict()
            if m.trades < 10:
                d.status, d.reasons = "UNVALIDATED", d.reasons + [f"TEST has only {m.trades} trades"]
            elif m.sharpe > 0 and m.total_return > 0 and m.profit_factor > 1:
                d.status = "ROBUST"
            else:
                d.status = "REJECTED"
                d.reasons.append(f"failed TEST: SR {m.sharpe:.2f}, PF {m.profit_factor:.2f}, return {m.total_return:.2%}")
            self._store(d)
        ranked = sorted(dossiers, key=lambda d: ({"ROBUST": 0, "UNVALIDATED": 1, "PASSED_SELECTION": 2}.get(d.status, 3),
                                                 -(d.score if math.isfinite(d.score) else -99)))
        robust = [d for d in ranked if d.status == "ROBUST"]
        if robust:
            top = robust[0]
            self.guard.request("final", "evaluate", f"final_oos:{top.genome.signature}")
            pre_final = slice(0, splits.bounds["test"][1])
            fm = ctx.backtest(top.genome, pre_final, splits.slice("final"), count=False).metrics
            top.final = fm.to_dict()
            if not (fm.sharpe > 0 and fm.profit_factor > 1 and fm.trades >= 5):
                top.reasons.append(f"FINAL out-of-sample failed: SR {fm.sharpe:.2f}, PF {fm.profit_factor:.2f}, "
                                   f"{fm.trades} trades")
            self._store(top)
        out.dossiers = [d.to_dict() for d in ranked]
        out.ranking = [d.to_dict() for d in ranked[:3]]
        fails: dict[str, int] = {}
        for d in dossiers:
            for a in d.attacks:
                if a.passed is False and a.kind != "warn":
                    fails[a.name] = fails.get(a.name, 0) + 1
        out.failure_summary = dict(sorted(fails.items(), key=lambda kv: -kv[1]))
        out.split_access = list(self.guard.log)
        self.memory.record_split_access(self.run_id, self.guard.log)

    def _refresh_deflated_sharpe(self, ctx: EvalContext, splits: DataSplits, dossiers: list[Dossier]) -> None:
        """Re-deflate every candidate with the trial count at the END of the search, so candidates examined
        early do not enjoy a smaller multiple-testing penalty. Can only make verdicts stricter."""
        n_trials, var = self.memory.trials(self.asset, self.dv)
        train = splits.slice("train")
        for d in dossiers:
            rets = ctx.backtest(d.genome, train, train, count=False).returns.to_numpy()
            ds_ = deflated_sharpe_report(rets, n_trials, var, ctx.market.ppy)
            d.overfit["deflated_sharpe"] = ds_
            for a in d.attacks:
                if a.name == "deflated_sharpe":
                    a.value, a.question = ds_["dsr"], f"Is the train Sharpe significant after {n_trials} trials?"
                    a.passed = bool(ds_["dsr"] >= self.cfg.robustness.min_deflated_sharpe_prob)
            before = d.status
            AdversarialEngine._verdict(d)
            if d.status != before:
                self._say(f"{d.strategy_id}: {before} -> {d.status} after re-deflating with {n_trials} trials")
            self._store(d)

    def _store(self, d: Dossier) -> None:
        payload = d.to_dict()
        payload["genome_signature"] = d.genome.signature
        self.memory.record_strategy(self.run_id, "", self.asset, self.dv, payload)

    def _scenario(self, ds: MarketDataset, ctx: EvalContext, pool: FeaturePool, validated: list[Hypothesis],
                  regimes: pd.Series | None) -> ScenarioReport:
        names = list(dict.fromkeys([h.feature for h in validated] + pool.confirmed))[:3]
        context_only = not names
        if context_only:
            names = [n for n in ("vol_20", "ret_20", "zdist_60") if n in ctx.prims]
        feats = {n: evaluate(pool.exprs[n], ctx.prims, ctx.cache) for n in names if n in pool.exprs}
        h = 5 if 5 in self.cfg.stats.horizons else self.cfg.stats.horizons[0]
        rep = scenario_analysis(self.asset, ds.bars["close"], feats, h, regimes)
        if context_only:
            rep.notes.insert(0, "No validated predictive condition exists; conditioning uses generic context "
                                "variables (volatility, recent return, distance to mean) only.")
        return rep

    def _verdict(self, out: ResearchOutcome) -> tuple[str, str]:
        robust = [d for d in out.dossiers if d["status"] == "ROBUST"]
        if robust:
            top = robust[0]
            fin = top.get("final") or {}
            if fin and (fin.get("sharpe") or 0) > 0 and (fin.get("profit_factor") or 0) > 1 and (fin.get("trades") or 0) >= 5:
                return ("EDGE FOUND (provisional)",
                        f"{top['strategy_id']} survived selection, adversarial attacks, TEST and FINAL out-of-sample. "
                        "Requires independent validation and paper trading before any real use.")
            return ("NO EDGE FOUND", f"{top['strategy_id']} passed TEST but failed the FINAL out-of-sample check.")
        n = len(out.dossiers)
        if n == 0:
            return ("NO EDGE FOUND", "No candidate reached positive, trade-sufficient fitness on TRAIN.")
        statuses = pd.Series([d["status"] for d in out.dossiers]).value_counts().to_dict()
        return ("NO EDGE FOUND", f"{n} candidate strategies examined; none survived. Outcome: {statuses}.")

    def _finish(self, out: ResearchOutcome, verdict: str, detail: str) -> ResearchOutcome:
        out.verdict, out.verdict_detail = verdict, detail
        out.elapsed_s = time.time() - self.t0
        out.budget = {**self.budget.model_dump(), "experiments_used": self.experiments, "strategies_examined": self.examined,
                      "minutes_used": round(out.elapsed_s / 60, 2), "mode": self.cfg.research.mode}
        out.limitations = self._limitations(out)
        if self.run_id:
            out.run_id = self.run_id
            self.memory.update_run(self.run_id, status="FINISHED", finished_at=pd.Timestamp.now(tz="UTC").isoformat(),
                                   verdict=verdict, summary={"detail": detail, "budget": out.budget})
            self._progress(phase="finished", verdict=verdict)
            self._say(f"{self.run_id}: finished - {verdict}: {detail}")
        return out

    @staticmethod
    def _limitations(out: ResearchOutcome) -> list[str]:
        lim = []
        caps = str(out.dataset.get("capabilities", ""))
        if "close only" in caps:
            lim.append("Price data is one close per day (Fed H.10 noon NY rate): no OHLC, no volume, no intraday; "
                       "stops are evaluated on closes only and execution is assumed at the next daily fix plus costs.")
        if not out.dataset.get("events"):
            lim.append("No economic calendar with consensus: surprise/expectation analysis could not run.")
        if not out.dataset.get("news"):
            lim.append("No news source: news intelligence could not run.")
        lim.append("Macro series are latest-vintage values with conservative publication lags (possible mild "
                   "revision look-ahead for revised series).")
        return lim
