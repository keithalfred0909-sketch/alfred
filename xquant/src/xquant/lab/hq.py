"""STRATEGY HQ: classification, Hall of Fame and Cemetery, read from the research memory (nothing estimated).

Tiers: DESTROYED (rejected or overfit - with cause of death), SURVIVING (passed selection, not yet TEST), VALIDATED
(passed TEST; or a pre-registered study with a provisional edge), ELITE (passed TEST and a FINAL out-of-sample that no
earlier run had opened). An empty Hall of Fame is reported as empty.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from xquant.memory.store import ResearchMemory, unpack

TIER = {"REJECTED": "DESTROYED", "OVERFIT": "DESTROYED", "PASSED_SELECTION": "SURVIVING", "UNVALIDATED": "SURVIVING",
        "ROBUST": "VALIDATED"}


def cause_of_death(reasons: list[str]) -> list[str]:
    """Attack names from the stored reasons ('attack: question -> value vs threshold')."""
    return [r.split(":", 1)[0].strip() for r in reasons if ":" in r]


def strategy_hq(mem: ResearchMemory, top: int = 10) -> dict[str, Any]:
    tiers: Counter[str] = Counter()
    causes: Counter[str] = Counter()
    first_cause: Counter[str] = Counter()
    fame, cemetery = [], []
    for r in mem.query("SELECT id, asset, status, description, score, reasons, created_at, dossier FROM strategies"):
        reasons = json.loads(r["reasons"] or "[]")
        tier = TIER.get(r["status"], "TESTING")
        d = unpack(r["dossier"], {})
        fin = d.get("final") or {}
        if tier == "VALIDATED" and fin and (fin.get("sharpe") or 0) > 0 and not any("not clean OOS" in x for x in reasons):
            tier = "ELITE"
        tiers[tier] += 1
        if tier == "DESTROYED":
            c = cause_of_death(reasons)
            causes.update(c)
            if c:
                first_cause[c[0]] += 1
            cemetery.append({"id": r["id"], "asset": r["asset"], "rules": r["description"], "died_of": c[:3],
                             "at": r["created_at"], "lineage_depth": len(d.get("lineage") or [])})
        else:
            fame.append({"id": r["id"], "asset": r["asset"], "tier": tier, "rules": r["description"], "score": r["score"]})
    for p in mem.query("SELECT name, asset, run_id, verdict FROM preregistrations WHERE verdict LIKE 'EDGE FOUND%'"):
        tiers["VALIDATED"] += 1
        fame.append({"id": p["name"], "asset": p["asset"], "tier": "VALIDATED (provisional, pre-registered study)",
                     "rules": f"see report of {p['run_id']}", "score": None, "verdict": p["verdict"]})
    fame.sort(key=lambda x: (x["tier"] != "ELITE", -(x["score"] or 0)))
    cemetery.sort(key=lambda x: x["at"] or "", reverse=True)
    return {"tiers": dict(tiers), "hall_of_fame": fame[:top] or "EMPTY - no strategy has survived validation",
            "cemetery": {"buried": tiers.get("DESTROYED", 0), "causes_any": dict(causes.most_common(12)),
                         "first_listed_cause": dict(first_cause.most_common(8)), "recent": cemetery[:top]}}
