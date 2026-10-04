"""CONFIRMATORY MODE: test a hypothesis written down BEFORE looking at any result.

Exploratory research pays for its breadth: the deflated Sharpe ratio counts every backtest ever run on
the dataset (often 10^5), so only a large effect can survive. A specific, pre-stated hypothesis does not
need that penalty - provided it really was stated first and is not tuned afterwards. This module
enforces that:

* A spec (YAML) lists a small, fixed set of strategy variants (<= MAX_VARIANTS). Its canonical SHA-256 is
  stored on first evaluation; re-running a spec of the same name with different content is refused
  (edit = new name, and every registration's variants keep counting).
* Multiple testing: N = all variants ever registered for this asset (the confirmatory family).
* Contamination: if any feature in the spec was already used by EXPLORATORY research (any asset), the
  test is not confirmatory and N falls back to every trial on the dataset - the exploratory penalty.
* Thresholds of tail conditions are fitted on TRAIN only; the full adversarial battery, TEST (once, for
  survivors) and FINAL (once, for the best) run exactly as in exploratory mode.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from xquant.adversarial.engine import AdversarialEngine, Dossier, score
from xquant.config import XQuantConfig
from xquant.data.engine import DataEngine
from xquant.errors import ConfigError, DataQualityError, DataUnavailableError, InsufficientDataError
from xquant.features.library import is_categorical, parse_key
from xquant.market.behavior import periods_per_year
from xquant.memory.store import ResearchMemory
from xquant.research.orchestrator import ResearchOrchestrator, ResearchOutcome
from xquant.strategy.genome import Genome
from xquant.validation.overfit import deflated_sharpe_report, pbo_cscv
from xquant.validation.splits import DataSplits, make_splits

MAX_VARIANTS = 20


def load_spec(path: str | Path) -> dict[str, Any]:
    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for key in ("name", "asset", "hypothesis", "variants"):
        if not spec.get(key):
            raise ConfigError(f"pre-registration spec needs '{key}'")
    if not 1 <= len(spec["variants"]) <= MAX_VARIANTS:
        raise ConfigError(f"a pre-registration lists 1..{MAX_VARIANTS} variants (got {len(spec['variants'])})")
    return spec


def spec_sha256(spec: dict[str, Any]) -> str:
    """Hash of everything that defines the test (free-text fields excluded only if absent)."""
    return hashlib.sha256(json.dumps(spec, sort_keys=True, default=str).encode()).hexdigest()


def spec_genomes(spec: dict[str, Any]) -> list[Genome]:
    out = []
    for i, v in enumerate(spec["variants"]):
        g = Genome.from_dict({"conditions": v["conditions"], "direction": v["direction"], "hold": v["hold"],
                              "stop": v.get("stop"), "take": v.get("take"), "trail": v.get("trail"),
                              "origin": f"prereg:{spec['name']}#{i + 1}"})
        if g.direction not in (-1, 1) or g.hold < 1:
            raise ConfigError(f"variant {i + 1}: direction must be +-1 and hold >= 1")
        out.append(g)
    if len({g.key() for g in out}) != len(out):
        raise ConfigError("duplicate variants in spec")
    return out


class ConfirmatoryStudy(ResearchOrchestrator):
    def __init__(self, cfg: XQuantConfig, spec: dict[str, Any], offline: bool = False,
                 memory: ResearchMemory | None = None, **kw: Any) -> None:
        super().__init__(cfg, offline=offline, memory=memory, **kw)
        if spec["asset"] != cfg.asset.symbol:
            raise ConfigError(f"spec is registered for {spec['asset']}, config is {cfg.asset.symbol}")
        self.spec = spec
        self.sha = spec_sha256(spec)
        self.genomes = spec_genomes(spec)
        self.features = sorted({c.feature for g in self.genomes for c in g.conditions})
        self._conf_n = 0

    def _run(self) -> ResearchOutcome:
        cfg, spec = self.cfg, self.spec
        out = ResearchOutcome(run_id="", asset=self.asset, verdict="", verdict_detail="")
        prior = self.memory.registration(spec["name"], self.asset)
        if prior and prior["sha256"] != self.sha:
            raise ConfigError(f"pre-registration '{spec['name']}' was already evaluated with different content "
                              f"(sha {prior['sha256'][:12]}); a registered test cannot be edited - register a new name")
        if prior and prior.get("run_id"):
            raise ConfigError(f"pre-registration '{spec['name']}' was already evaluated in {prior['run_id']} "
                              f"({prior['verdict']}); a confirmatory test runs once")
        t = time.time()
        try:
            ds = self._dataset or DataEngine(cfg.asset, offline=self.offline).load()
        except (DataUnavailableError, DataQualityError) as exc:
            self.run_id = self.memory.start_run(self.asset, "confirmatory", "n/a", self.cfp, cfg.research.seed)
            self._experiment("data", "data", {}, {}, f"data unavailable or failed validation: {exc}", "FAILED", t)
            return self._finish(out, "INSUFFICIENT DATA", f"Data could not be loaded or validated: {exc}")
        self.dv = ds.version
        # Contamination is judged BEFORE this study writes anything to memory.
        # (A resumed registration keeps its original judgement: its own earlier attempt is not exploration.)
        explored = {f: self.memory.feature_explored(f) for f in self.features}
        contaminated = (json.loads(prior["contaminated"] or "[]") if prior
                        else sorted(f for f, hits in explored.items() if hits))
        if not prior:
            self.memory.register(spec["name"], self.asset, self.dv, self.sha, spec, len(self.genomes), contaminated)
        self.run_id = self.memory.start_run(self.asset, "confirmatory", self.dv, self.cfp, cfg.research.seed)
        out.run_id = self.run_id
        out.dataset = {**ds.summary(), "quality_report": ds.quality.to_dict(), "notes": ds.meta.notes,
                       "exogenous_meta": ds.exog_meta}
        self._say(f"{self.run_id}: confirmatory study '{spec['name']}' on {self.asset}; dataset {self.dv}; "
                  f"spec sha256 {self.sha[:16]}; {len(self.genomes)} variants")
        try:
            splits = make_splits(pd.DatetimeIndex(ds.bars.index), cfg.asset.splits)
        except InsufficientDataError as exc:
            return self._finish(out, "INSUFFICIENT DATA", str(exc))
        out.splits = {k: {"span": splits.span(k), "bars": v} for k, v in splits.sizes().items()}  # type: ignore[arg-type]

        ppy = periods_per_year(pd.DatetimeIndex(ds.bars.index))
        exprs = {f: parse_key(f) for f in self.features}
        ctx = self._build_context(ds.bars, ds.exog, exprs, None, ppy)
        missing = [f for f in self.features if not exprs[f].primitives() <= set(ctx.prims)]
        if missing:
            return self._finish(out, "INSUFFICIENT DATA", f"features not available in this dataset: {missing}")
        self._lookahead_audit(ds, ctx, sorted({p for f in self.features for p in exprs[f].primitives()}))

        family = self.memory.registered_variants(self.asset)
        if contaminated:
            n_expl, _ = self.memory.trials(self.asset, self.dv)
            self._conf_n = n_expl + family
            self._say(f"CONTAMINATED: {contaminated} already used by exploratory research -> not confirmatory; "
                      f"multiple-testing N = all {self._conf_n} trials on this dataset")
        else:
            self._conf_n = family
            self._say(f"clean pre-registration: multiple-testing N = {family} registered variant(s) for {self.asset}")
        out.preregistration = {"name": spec["name"], "sha256": self.sha, "hypothesis": spec["hypothesis"],
                               "rationale": spec.get("rationale", ""), "registered_by": spec.get("registered_by", ""),
                               "registered_at": (prior or {}).get("registered_at") or pd.Timestamp.now(tz="UTC").isoformat(),
                               "variants": [g.describe() for g in self.genomes], "features": self.features,
                               "contaminated_features": {f: explored[f] for f in contaminated},
                               "multiple_testing_n": self._conf_n,
                               "categorical_features": [f for f in self.features if is_categorical(f)]}

        train = splits.slice("train")
        srs = [ctx.backtest(g, train, train).metrics.sharpe for g in self.genomes]
        self.memory.add_trials(self.asset, self.dv, srs)  # also tightens later exploratory runs
        pbo = self._variants_pbo(ctx, train)
        rebuild = lambda bars: self._build_context(bars, ds.exog, exprs, None, ppy * len(bars) / len(ds.bars))  # noqa: E731
        adv = AdversarialEngine(ctx, splits, self.guard, cfg.robustness, rebuild, ds.bars, cfg.asset.timezone,
                                cfg.stats.min_trades, np.random.default_rng(cfg.research.seed + 1),
                                min_trades_per_day=cfg.stats.min_trades_per_day)
        round_trip = 2 * (cfg.asset.costs.spread_bps / 2 + cfg.asset.costs.commission_bps
                          + cfg.asset.costs.slippage_bps) * 1e-4
        dossiers: list[Dossier] = []
        eid = self._experiment("confirmatory", "preregistered", {"spec": spec["name"], "sha256": self.sha,
                                                                 "variants": len(self.genomes)},
                               {"multiple_testing_n": self._conf_n, "contaminated": contaminated},
                               "pre-registered variants examined", "OK", t)
        for g in self.genomes:
            d = adv.examine(g, self._conf_n, 0.0, pbo)
            d.score = score(d, round_trip)
            self.examined += 1
            payload = d.to_dict()
            payload["genome_signature"] = g.signature
            d.strategy_id = self.memory.record_strategy(self.run_id, eid, self.asset, self.dv, payload)
            dossiers.append(d)
            self._say(f"{d.strategy_id} {g.describe()} -> {d.status}")
        self._final_stage(ctx, splits, dossiers, out)
        out.trials = {"n_trials": self._conf_n, "family": "confirmatory" if not contaminated else "exploratory"}
        verdict, detail = self._verdict(out)
        self.memory.complete_registration(spec["name"], self.asset, self.run_id, verdict)
        return self._finish(out, verdict, f"[pre-registered '{spec['name']}', N={self._conf_n}] {detail}")

    def _variants_pbo(self, ctx: Any, train: slice) -> dict[str, Any]:
        if len(self.genomes) < 4:
            return {"status": "INSUFFICIENT DATA", "note": "PBO needs >= 4 variants"}
        mat = np.column_stack([ctx.backtest(g, train, train, count=False).returns.to_numpy() for g in self.genomes])
        return pbo_cscv(mat)

    def _refresh_deflated_sharpe(self, ctx: Any, splits: DataSplits, dossiers: list[Dossier]) -> None:
        """Same as exploratory mode but with the confirmatory family's N."""
        train = splits.slice("train")
        for d in dossiers:
            rets = ctx.backtest(d.genome, train, train, count=False).returns.to_numpy()
            ds_ = deflated_sharpe_report(rets, self._conf_n, 0.0, ctx.market.ppy)
            d.overfit["deflated_sharpe"] = ds_
            for a in d.attacks:
                if a.name == "deflated_sharpe":
                    a.value, a.question = ds_["dsr"], f"Is the train Sharpe significant after {self._conf_n} trials?"
                    a.passed = bool(ds_["dsr"] >= self.cfg.robustness.min_deflated_sharpe_prob)
            AdversarialEngine._verdict(d)
            self._store(d)


def summarise(out: ResearchOutcome) -> str:
    def sr(m: dict[str, Any]) -> str:
        v = m.get("sharpe")
        return "n/a" if v is None else f"{v:.2f}"
    rows = []
    for d in out.dossiers:
        v = d.get("validation") or {}
        t = d.get("train") or {}
        fails = [a["name"] for a in d.get("attacks", []) if a.get("passed") is False and a.get("kind") != "warn"]
        rows.append(f"{d.get('strategy_id')}: {d['status']} | train SR {sr(t)} "
                    f"({t.get('trades')} tr) | val SR {sr(v)} ({v.get('trades')} tr) | "
                    f"failed: {', '.join(fails) or '-'}")
    return "\n".join(rows)
