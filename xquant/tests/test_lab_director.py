"""Research Director: pending specs first, coverage by shared price source, follow-ups, escalation of failures."""

from xquant.lab import director as dr
from xquant.lab.queue import Queue
from xquant.memory.store import ResearchMemory


def _mem(tmp_path):
    mem = ResearchMemory(tmp_path / "m.db")
    return mem


def test_plan_prefers_unevaluated_specs_and_respects_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr(dr, "data_available", lambda asset, depth=0: True)
    mem = _mem(tmp_path)
    plan = dr.make_plan(mem, max_new=100)
    kinds = [d.kind for d in plan.decisions]
    assert kinds[0] in ("confirm", "allocate", "daytrade", "ml") and plan.decisions[0].priority == "HIGH_VALUE"
    specs = [d.params["spec"] for d in plan.decisions if "spec" in d.params]
    assert not any("nq_orb5_v1" in s for s in specs)  # superseded specs are never run
    assets = {d.params.get("asset") for d in plan.decisions if d.kind == "research"}
    assert "EURUSD_H1" in assets and "NAS100_M1" not in assets  # minute bars are bases, not targets
    # an exploratory run on EURUSD_H1 also covers the configs that share its price source (RV, DXY)
    rid = mem.start_run("EURUSD_H1", "standard", "v", "fp", 0)
    mem.update_run(rid, status="FINISHED", verdict="NO EDGE FOUND")
    assets = {d.params.get("asset") for d in dr.make_plan(mem, max_new=100).decisions if d.kind == "research"}
    assert not assets & {"EURUSD_H1", "EURUSD_H1_RV", "EURUSD_H1_DXY"}
    assert len(dr.make_plan(mem, max_new=2).decisions) == 2


def test_failed_jobs_are_escalated_not_retried_forever(tmp_path, monkeypatch):
    monkeypatch.setattr(dr, "data_available", lambda asset, depth=0: True)
    mem = _mem(tmp_path)
    q = Queue(tmp_path / "m.db")
    plan = dr.make_plan(mem, max_new=1)
    jid, created, d = dr.enqueue(plan, q)[0]
    assert created
    w = q.register_worker(None)
    q.claim(w)
    q.conn.execute("UPDATE jobs SET attempts=max_attempts WHERE id=?", (jid,))
    q.finish(jid, False, error="data missing")
    plan2 = dr.make_plan(mem, max_new=1)
    assert dr.enqueue(plan2, q) == [] and any("already FAILED" in h for h in plan2.human_actions)
