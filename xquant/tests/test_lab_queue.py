"""Research queue and workers: ordering, dependencies, dedupe, retries, timeouts, crash recovery, real status."""

import sys
from datetime import UTC, datetime, timedelta

import pytest

from xquant.lab import queue as lq
from xquant.lab.queue import JobKind, Queue, execute, lab_status, run_worker


@pytest.fixture
def kinds(monkeypatch):
    """Test-only job kinds: plain python one-liners instead of research commands."""
    py = sys.executable
    extra = {
        "ok": JobKind("test_dept", lambda p, db: [py, "-c", "print('NO EDGE FOUND: fine'); print('report: r.md')"], 30, 0.1),
        "fail": JobKind("test_dept", lambda p, db: [py, "-c", "import sys; print('boom'); sys.exit(3)"], 30, 0.1),
        "slow": JobKind("test_dept", lambda p, db: [py, "-c", "import time; time.sleep(30)"], 2, 0.1),
    }
    monkeypatch.setattr(lq, "KINDS", {**lq.KINDS, **extra})


def test_priority_dependencies_and_dedupe(tmp_path, kinds):
    q = Queue(tmp_path / "m.db")
    a, created = q.add("ok", {"x": 1}, priority="LOW")
    assert created
    assert q.add("ok", {"x": 1}) == (a, False)  # identical experiment refused while queued
    b, _ = q.add("ok", {"x": 2}, priority="URGENT", depends_on=[a])
    c, _ = q.add("ok", {"x": 3}, priority="HIGH_VALUE")
    w = q.register_worker(None)
    assert q.claim(w)["id"] == c  # URGENT b is blocked by its dependency
    q.finish(c, True)
    assert q.claim(w)["id"] == a
    q.finish(a, True)
    assert q.claim(w)["id"] == b  # dependency now DONE
    q.finish(b, True)
    assert q.add("ok", {"x": 1}) == (a, False)  # DONE experiments are not repeated either
    assert q.add("ok", {"x": 1}, force=True)[1]


def test_retry_then_escalate_and_logs(tmp_path, kinds):
    q = Queue(tmp_path / "m.db")
    jid, _ = q.add("fail", {}, max_attempts=2)
    w = q.register_worker(None)
    assert execute(q, w, q.claim(w), log_dir=tmp_path) == "QUEUED"  # retried with back-off
    q.conn.execute("UPDATE jobs SET not_before=NULL WHERE id=?", (jid,))
    assert execute(q, w, q.claim(w), log_dir=tmp_path) == "FAILED"
    j = q.get(jid)
    assert j["attempts"] == 2 and "boom" in j["error"] and (tmp_path / f"{jid}.attempt2.log").exists()


def test_timeout_kills_the_job(tmp_path, kinds):
    q = Queue(tmp_path / "m.db")
    jid, _ = q.add("slow", {}, max_attempts=1)
    w = q.register_worker(None)
    assert execute(q, w, q.claim(w), heartbeat_s=0.5, log_dir=tmp_path) == "FAILED"
    assert "timeout" in q.get(jid)["error"]


def test_dead_worker_job_is_recovered(tmp_path, kinds):
    q = Queue(tmp_path / "m.db")
    jid, _ = q.add("ok", {}, max_attempts=3)
    w = q.register_worker(None)
    q.claim(w)  # the worker "dies" here: no heartbeat, no finish
    old = (datetime.now(UTC) - timedelta(minutes=10)).isoformat(timespec="seconds")
    q.conn.execute("UPDATE jobs SET heartbeat_at=? WHERE id=?", (old, jid))
    q.conn.execute("UPDATE workers SET heartbeat_at=? WHERE id=?", (old, w))
    assert q.recover_stale(300) == [jid]
    assert q.get(jid)["status"] == "QUEUED" and "worker lost" in q.get(jid)["error"]
    assert q.conn.execute("SELECT status FROM workers WHERE id=?", (w,)).fetchone()[0] == "DEAD"


def test_worker_loop_and_status_are_real(tmp_path, kinds):
    db = tmp_path / "m.db"
    q = Queue(db)
    q.add("ok", {"n": 1})
    q.add("ok", {"n": 2})
    st = lab_status(db)
    assert st["lab"].startswith("OFFLINE") and st["active_agents"] == 0 and st["jobs"] == {"QUEUED": 2}
    counts = run_worker(db, max_jobs=2, poll_s=0.1, log=lambda s: None)
    assert counts == {"done": 2, "failed": 0, "requeued": 0}
    st = lab_status(db)
    assert st["jobs"] == {"DONE": 2} and st["active_agents"] == 0  # the worker stopped: no fake activity
    assert lq.Queue(db).get("JOB-000001")["result"].count("NO EDGE FOUND") == 1


def test_research_job_command_uses_existing_cli():
    argv = lq.KINDS["research"].build({"asset": "EURUSD_H1", "max_minutes": 5, "focus": ["x_px_"]}, "m.db")
    assert argv[1:4] == ["-m", "xquant.cli", "research"] and "--offline" in argv and argv[argv.index("--focus") + 1] == "x_px_"


def test_alerts_are_raised_once_and_shown_in_status(tmp_path, kinds):
    db = tmp_path / "m.db"
    q = Queue(db)
    jid, _ = q.add("fail", {}, max_attempts=1)
    w = q.register_worker(None)
    execute(q, w, q.claim(w), log_dir=tmp_path)
    assert [a["level"] for a in q.alerts()] == ["ERROR"]
    assert not q.alert("ERROR", jid, q.alerts()[0]["message"])  # same open alert is not duplicated
    assert len(lab_status(db)["open_alerts"]) == 1
    assert q.acknowledge() == 1 and lab_status(db)["open_alerts"] == []


def test_dashboard_control_center_shows_real_state(tmp_path, kinds):
    from xquant.dashboard.render import build_html
    from xquant.memory.store import ResearchMemory
    db = tmp_path / "m.db"
    Queue(db).add("ok", {})
    html = build_html(ResearchMemory(db))
    assert "Control center" in html and "IDLE - no worker running" in html and ">OFFLINE<" in html
