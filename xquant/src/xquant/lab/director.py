"""RESEARCH DIRECTOR: decides what the lab researches next, from the research memory and the queue.

Deterministic and auditable - every decision carries its reason (stored in the job). Policies, in order:
1. Pre-registered specs committed but never evaluated -> run them (HIGH_VALUE: clean, cheap, small N).
2. Coverage gaps: an asset/timeframe whose price data is available offline and that no exploratory run has
   covered (configs sharing the same price source count as covered) -> standard exploratory run.
3. Evidence follow-up: a covered asset with validated hypotheses but no deep run -> deep run (budgeted).
4. Maintenance: memory database near the git size limit -> compaction.
It never downloads data on its own (the user asked not to fetch unnecessary data), never repeats an identical job
(queue dedupe) and never re-runs an exhausted line. What needs a human is reported, not done.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from xquant.config import PROJECT_ROOT, load_config
from xquant.lab.queue import Queue, dedupe_key
from xquant.memory.store import ResearchMemory

MIN_EXPLORATORY_MINUTES = 5  # minute bars are bases for resampling, not exploratory targets
EXPLORATORY_MODES = ("quick", "standard", "deep")


@dataclass
class Decision:
    kind: str
    params: dict[str, Any]
    priority: str
    reason: str


@dataclass
class Plan:
    decisions: list[Decision] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    human_actions: list[str] = field(default_factory=list)


def _timeframe_minutes(tf: str) -> float:
    tf = tf.lower()
    for unit, m in (("min", 1), ("h", 60), ("d", 1440)):
        if tf.endswith(unit):
            try:
                return float(tf[: -len(unit)] or 1) * m
            except ValueError:
                return 0.0
    return 0.0


def data_available(asset: str, depth: int = 0) -> bool:
    """Cheap offline check (no loading): is the price data of this config already on disk?"""
    if depth > 3:
        return False
    try:
        src = load_config(asset).asset.price_source
    except Exception:
        return False
    p = src.params
    if src.kind == "dukascopy_candles":
        d = PROJECT_ROOT / "cache" / "dukascopy_candles" / str(p["instrument"]).upper() / p.get("granularity", "hour") / "BID"
        return d.is_dir() and any(d.glob("*.bi5"))
    if src.kind == "resample_asset":
        return data_available(str(p["asset"]), depth + 1)
    if p.get("snapshot"):
        return (PROJECT_ROOT / "datasets" / str(p["snapshot"])).exists()
    if p.get("path"):
        return (PROJECT_ROOT / str(p["path"])).exists()
    return False


def _asset_catalog() -> dict[str, dict[str, Any]]:
    out = {}
    for f in sorted((PROJECT_ROOT / "configs" / "assets").glob("*.yaml")):
        try:
            a = load_config(f.stem).asset
        except Exception:
            continue
        out[a.symbol] = {"config": f.stem, "timeframe": a.timeframe,
                         "source": json.dumps({"kind": a.price_source.kind, **a.price_source.params}, sort_keys=True, default=str)}
    return out


def _pending_specs(mem: ResearchMemory) -> list[tuple[str, str, str]]:
    """(kind, path, name) of committed specs never evaluated."""
    done = {r["name"] for r in mem.query("SELECT name FROM preregistrations WHERE run_id IS NOT NULL")}
    out = []
    for folder in ("preregistered", "strategies"):
        for f in sorted((PROJECT_ROOT / "configs" / folder).glob("*.yaml")):
            text = f.read_text(encoding="utf-8")
            if text.startswith("# SUPERSEDED"):
                continue
            spec = yaml.safe_load(text) or {}
            name = spec.get("name")
            if not name or name in done:
                continue
            if folder == "strategies":
                kind = "daytrade"
            elif spec.get("kind") in ("vol_managed", "tsmom", "xs_momentum"):
                kind = "allocate"
            elif spec.get("model"):
                kind = "ml"
            else:
                kind = "confirm"
            out.append((kind, str(f.relative_to(PROJECT_ROOT)), str(name)))
    return out


def make_plan(mem: ResearchMemory, max_new: int = 5, deep_min_validated: int = 10) -> Plan:
    plan = Plan()
    for kind, path, name in _pending_specs(mem):
        plan.decisions.append(Decision(kind, {"spec": path}, "HIGH_VALUE",
                                       f"pre-registered spec '{name}' is committed but has never been evaluated"))
    runs = mem.query("SELECT asset, mode, verdict FROM research_runs")
    explored = {r["asset"] for r in runs if r["mode"] in EXPLORATORY_MODES and r["verdict"] not in (None, "FAILED", "ABORTED")}
    deep_done = {r["asset"] for r in runs if r["mode"] == "deep" and r["verdict"] not in (None, "FAILED")}
    catalog = _asset_catalog()
    covered_sources = {catalog[a]["source"] for a in explored if a in catalog}
    deep_sources = {catalog[a]["source"] for a in deep_done if a in catalog}
    validated = {r["asset"]: int(r["n"]) for r in mem.query(
        "SELECT asset, COUNT(*) AS n FROM hypotheses WHERE status='VALIDATION' GROUP BY asset")}
    for sym, info in catalog.items():
        if sym in explored or info["source"] in covered_sources:
            continue
        if _timeframe_minutes(info["timeframe"]) < MIN_EXPLORATORY_MINUTES:
            plan.skipped.append(f"{sym}: {info['timeframe']} bars are a base for resampling, not an exploratory target")
            continue
        if not data_available(info["config"]):
            plan.skipped.append(f"{sym}: price data not on disk (not downloaded automatically)")
            continue
        plan.decisions.append(Decision("research", {"asset": sym, "mode": "standard", "max_minutes": 45}, "EXPLORATORY",
                                       f"coverage gap: no exploratory run on {sym} ({info['timeframe']}) and its data is available"))
    for sym, n in sorted(validated.items(), key=lambda kv: -kv[1]):
        if (sym in catalog and sym not in deep_done and catalog[sym]["source"] not in deep_sources
                and n >= deep_min_validated and data_available(catalog[sym]["config"])):
            plan.decisions.append(Decision("research", {"asset": sym, "mode": "deep", "max_minutes": 120}, "NORMAL",
                                           f"evidence follow-up: {n} hypotheses passed FDR + inner holdout on {sym}, no deep run yet"))
    db = Path(mem.path)
    if db.exists() and db.stat().st_size > 45e6:
        plan.decisions.append(Decision("compact", {}, "LOW", f"memory database is {db.stat().st_size / 1e6:.0f} MB (git limit 100 MB)"))
    for r in mem.query("SELECT name, run_id FROM preregistrations WHERE verdict LIKE 'EDGE FOUND%'"):
        plan.human_actions.append(f"'{r['name']}' ({r['run_id']}) has a provisional edge: needs independent validation "
                                  "(MT5 Strategy Tester on broker data) and demo paper trading - human step")
    plan.decisions = plan.decisions[:max_new]
    return plan


def enqueue(plan: Plan, q: Queue) -> list[tuple[str, bool, Decision]]:
    """Queue the plan. A decision whose identical job already FAILED is escalated to a human, not retried forever."""
    out = []
    for d in plan.decisions:
        failed = q.conn.execute("SELECT id, error FROM jobs WHERE dedupe_key=? AND status='FAILED' ORDER BY created_at DESC",
                                (dedupe_key(d.kind, d.params),)).fetchone()
        if failed:
            last = (failed["error"] or "").strip().splitlines()[-1:] or [""]
            plan.human_actions.append(f"{d.kind} {d.params} already FAILED ({failed['id']}: {last[0][:120]}) - needs a look")
            continue
        jid, created = q.add(d.kind, d.params, priority=d.priority, reason=d.reason)
        out.append((jid, created, d))
    return out
