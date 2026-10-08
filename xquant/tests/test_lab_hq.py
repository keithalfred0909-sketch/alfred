"""Strategy HQ tiers / cemetery and evolution genealogy."""

import json

import numpy as np

from xquant.evolution.engine import EvolutionEngine, Individual
from xquant.lab.hq import strategy_hq
from xquant.memory.store import ResearchMemory, pack
from xquant.strategy.genome import Condition, Genome


def test_tiers_cemetery_and_provisional_edges(tmp_path):
    mem = ResearchMemory(tmp_path / "m.db")
    rows = [("S1", "REJECTED", ["deflated_sharpe: q -> 0.1 vs 0.95", "walk_forward: q"], {}),
            ("S2", "OVERFIT", ["deflated_sharpe: q"], {}),
            ("S3", "ROBUST", [], {"final": {"sharpe": 0.8}}),
            ("S4", "ROBUST", ["FINAL ... not clean OOS"], {"final": {"sharpe": 0.8}})]
    for sid, status, reasons, dossier in rows:
        mem.conn.execute("INSERT INTO strategies (id, signature, asset, dataset_version, status, description, reasons, score,"
                         " dossier, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (sid, sid, "A", "v", status, "rule", json.dumps(reasons), 1.0, pack(dossier), "2026-10-08"))
    mem.register("spec_x", "DAYTRADE:X", "v", "sha", {}, 2, [])
    mem.complete_registration("spec_x", "DAYTRADE:X", "RUN-9", "EDGE FOUND (provisional)")
    mem.conn.commit()
    hq = strategy_hq(mem)
    assert hq["tiers"] == {"DESTROYED": 2, "ELITE": 1, "VALIDATED": 2}  # S4 reused FINAL: not elite
    assert hq["cemetery"]["causes_any"]["deflated_sharpe"] == 2 and hq["cemetery"]["first_listed_cause"] == {"deflated_sharpe": 2}
    assert hq["hall_of_fame"][0]["id"] == "S3"
    assert ResearchMemory(tmp_path / "e.db") and strategy_hq(ResearchMemory(tmp_path / "e.db"))["hall_of_fame"].startswith("EMPTY")


def test_ancestry_follows_mutations_and_crossovers():
    eng = EvolutionEngine.__new__(EvolutionEngine)  # only the genealogy bookkeeping is exercised
    a = Genome((Condition("ret_5", "low", 0.1),), 1, 5)
    b = Genome((Condition("vol_20", "high", 0.2),), -1, 3)
    child = Genome((Condition("ret_5", "low", 0.1), Condition("vol_20", "high", 0.2)), 1, 5, origin="crossover",
                   parents=(a.signature, b.signature), mutation="crossover")
    grand = Genome(child.conditions, 1, 8, origin="mutation", parents=(child.signature,), mutation="hold")
    eng.cache = {g.key(): Individual(g, float(f)) for g, f in ((a, 0.1), (b, 0.2), (child, 0.3), (grand, 0.4))}
    line = eng.ancestry(grand)
    assert [x["signature"] for x in line] == [grand.signature, child.signature, a.signature, b.signature]
    assert line[0]["mutation"] == "hold" and line[1]["mutation"] == "crossover" and np.isclose(line[0]["fitness"], 0.4)
    assert grand.key() == Genome(child.conditions, 1, 8).key()  # genealogy never changes the identity/dedupe key
