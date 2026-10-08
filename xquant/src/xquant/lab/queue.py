"""RESEARCH QUEUE + WORKERS: persistent jobs that survive crashes, with retries, timeouts and heartbeats.

A job is one existing lab command (research / confirm / allocate / daytrade / ml / data / compact) run in its own
subprocess, so a crash, a hang or a memory blow-up kills only that job. Workers are the lab's "agents": every row in
``workers`` is a real process with a heartbeat, and a job is RUNNING only while a live worker is executing it -
the status the dashboard shows is read from here, never invented.

Self-healing: DETECT (stale heartbeat / non-zero exit / timeout) -> LOG (error + log file) -> RETRY (back-off,
``max_attempts``) -> RECOVER (stale RUNNING jobs are re-queued) -> ESCALATE (FAILED after the last attempt).
Duplicate experiments are refused by a dedupe key (kind + parameters) unless explicitly forced.
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from xquant.config import PROJECT_ROOT

PRIORITIES = {"URGENT": 0, "HIGH_VALUE": 1, "NORMAL": 2, "EXPLORATORY": 3, "LOW": 4}
ACTIVE = ("QUEUED", "RUNNING", "DONE")  # a duplicate of one of these is refused

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY, kind TEXT NOT NULL, department TEXT NOT NULL, priority INTEGER NOT NULL, status TEXT NOT NULL,
  params TEXT NOT NULL, depends_on TEXT NOT NULL, dedupe_key TEXT NOT NULL, reason TEXT, attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL, timeout_s INTEGER NOT NULL, cost_estimate_min REAL, worker TEXT, not_before TEXT,
  created_at TEXT NOT NULL, started_at TEXT, heartbeat_at TEXT, finished_at TEXT, result TEXT, error TEXT, log_path TEXT);
CREATE INDEX IF NOT EXISTS jobs_status ON jobs(status, priority, created_at);
CREATE TABLE IF NOT EXISTS workers (
  id TEXT PRIMARY KEY, department TEXT, pid INTEGER, host TEXT, status TEXT, current_job TEXT, started_at TEXT,
  heartbeat_at TEXT, jobs_done INTEGER NOT NULL DEFAULT 0, jobs_failed INTEGER NOT NULL DEFAULT 0);
"""


def _now() -> datetime:
    return datetime.now(UTC)


def _iso(t: datetime) -> str:
    return t.isoformat(timespec="seconds")


def _cli(*args: str) -> list[str]:
    return [sys.executable, "-m", "xquant.cli", *args]


def _opt(flag: str, value: Any) -> list[str]:
    if value is None or value is False:
        return []
    if value is True:
        return [flag]
    if isinstance(value, list):
        return [flag, *map(str, value)]
    return [flag, str(value)]


@dataclass(frozen=True)
class JobKind:
    department: str
    build: Callable[[dict[str, Any], str], list[str]]  # (params, memory_db) -> argv
    timeout_s: int
    cost_estimate_min: float


KINDS: dict[str, JobKind] = {
    "research": JobKind("pattern_mining", lambda p, db: _cli(
        "research", "--asset", p["asset"], "--memory", db, *_opt("--mode", p.get("mode", "standard")),
        *_opt("--offline", p.get("offline", True)), *_opt("--max-minutes", p.get("max_minutes")),
        *_opt("--min-trades-per-day", p.get("min_trades_per_day")), *_opt("--focus", p.get("focus")),
        *_opt("--seed", p.get("seed"))), 4 * 3600, 60.0),
    "confirm": JobKind("hypothesis_lab", lambda p, db: _cli(
        "confirm", "--spec", p["spec"], "--memory", db, *_opt("--offline", p.get("offline", True))), 3600, 10.0),
    "allocate": JobKind("strategy_factory", lambda p, db: _cli(
        "allocate", "--spec", p["spec"], "--memory", db, *_opt("--offline", p.get("offline", True))), 3600, 5.0),
    "daytrade": JobKind("strategy_factory", lambda p, db: _cli(
        "daytrade", "--spec", p["spec"], "--memory", db, *_opt("--offline", p.get("offline", True))), 3600, 10.0),
    "ml": JobKind("pattern_mining", lambda p, db: _cli(
        "ml", "--spec", p["spec"], "--memory", db, *_opt("--offline", p.get("offline", True))), 2 * 3600, 30.0),
    "data": JobKind("data_mining", lambda p, db: _cli(
        "data", "validate", "--asset", p["asset"], *_opt("--offline", p.get("offline", False))), 2 * 3600, 30.0),
    "compact": JobKind("research_memory", lambda p, db: _cli("memory", "compact", "--memory", db), 1800, 2.0),
}


def dedupe_key(kind: str, params: dict[str, Any]) -> str:
    return hashlib.sha1(f"{kind}|{json.dumps(params, sort_keys=True, default=str)}".encode()).hexdigest()[:16]


class Queue:
    def __init__(self, db: str | Path) -> None:
        self.db = str(db)
        self.conn = sqlite3.connect(self.db, timeout=30, isolation_level=None)  # explicit transactions below
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def _next_id(self, prefix: str) -> str:
        self.conn.execute("CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
        self.conn.execute("INSERT INTO counters(name, value) VALUES (?, 1) ON CONFLICT(name) DO UPDATE SET value = value + 1",
                          (prefix,))
        v = self.conn.execute("SELECT value FROM counters WHERE name = ?", (prefix,)).fetchone()[0]
        return f"{prefix}-{v:06d}"

    # ---- enqueue / inspect ---------------------------------------------------------------------------
    def add(self, kind: str, params: dict[str, Any], priority: str = "NORMAL", depends_on: list[str] | None = None,
            reason: str = "", max_attempts: int = 3, timeout_s: int | None = None, force: bool = False) -> tuple[str, bool]:
        """Returns (job id, created). An identical job already queued/running/done is returned instead of duplicated."""
        if kind not in KINDS:
            raise ValueError(f"unknown job kind {kind!r}; known: {sorted(KINDS)}")
        if priority not in PRIORITIES:
            raise ValueError(f"priority must be one of {list(PRIORITIES)}")
        key = dedupe_key(kind, params)
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            if not force:
                dup = self.conn.execute(f"SELECT id FROM jobs WHERE dedupe_key=? AND status IN ({','.join('?' * len(ACTIVE))})",
                                        (key, *ACTIVE)).fetchone()
                if dup:
                    self.conn.execute("COMMIT")
                    return dup["id"], False
            jk = KINDS[kind]
            jid = self._next_id("JOB")
            self.conn.execute(
                "INSERT INTO jobs (id, kind, department, priority, status, params, depends_on, dedupe_key, reason, max_attempts,"
                " timeout_s, cost_estimate_min, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (jid, kind, jk.department, PRIORITIES[priority], "QUEUED", json.dumps(params, sort_keys=True),
                 json.dumps(depends_on or []), key, reason, max_attempts, timeout_s or jk.timeout_s, jk.cost_estimate_min,
                 _iso(_now())))
            self.conn.execute("COMMIT")
            return jid, True
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def get(self, jid: str) -> dict[str, Any]:
        r = self.conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
        if r is None:
            raise KeyError(jid)
        return dict(r)

    def jobs(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        sql, args = "SELECT * FROM jobs", cast(tuple[str, ...], ())
        if status:
            sql, args = sql + " WHERE status=?", (status,)
        return [dict(r) for r in self.conn.execute(sql + " ORDER BY created_at DESC LIMIT ?", (*args, limit))]

    def cancel(self, jid: str) -> bool:
        cur = self.conn.execute("UPDATE jobs SET status='CANCELLED', finished_at=? WHERE id=? AND status='QUEUED'",
                                (_iso(_now()), jid))
        return cur.rowcount == 1

    # ---- workers -----------------------------------------------------------------------------------------
    def register_worker(self, department: str | None) -> str:
        wid = f"W-{socket.gethostname()[:12]}-{os.getpid()}-{int(time.time()) % 100000}"
        self.conn.execute("INSERT OR REPLACE INTO workers (id, department, pid, host, status, started_at, heartbeat_at)"
                          " VALUES (?,?,?,?,?,?,?)", (wid, department or "any", os.getpid(), socket.gethostname(), "IDLE",
                                                      _iso(_now()), _iso(_now())))
        return wid

    def worker_beat(self, wid: str, status: str, job: str | None) -> None:
        self.conn.execute("UPDATE workers SET status=?, current_job=?, heartbeat_at=? WHERE id=?",
                          (status, job, _iso(_now()), wid))

    def claim(self, wid: str, department: str | None = None) -> dict[str, Any] | None:
        """Atomically take the best runnable job: QUEUED, back-off elapsed, all dependencies DONE."""
        now = _iso(_now())
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            rows = self.conn.execute(
                "SELECT * FROM jobs WHERE status='QUEUED' AND (not_before IS NULL OR not_before<=?)"
                + (" AND department=?" if department else "") + " ORDER BY priority, created_at",
                (now, department) if department else (now,)).fetchall()
            for r in rows:
                deps = json.loads(r["depends_on"])
                if deps:
                    done = self.conn.execute(f"SELECT COUNT(*) FROM jobs WHERE status='DONE' AND id IN ({','.join('?' * len(deps))})",
                                             deps).fetchone()[0]
                    if done != len(deps):
                        continue
                self.conn.execute("UPDATE jobs SET status='RUNNING', worker=?, attempts=attempts+1, started_at=?, heartbeat_at=?"
                                  " WHERE id=?", (wid, now, now, r["id"]))
                self.conn.execute("COMMIT")
                return self.get(r["id"])
            self.conn.execute("COMMIT")
            return None
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def job_beat(self, jid: str) -> None:
        self.conn.execute("UPDATE jobs SET heartbeat_at=? WHERE id=?", (_iso(_now()), jid))

    def finish(self, jid: str, ok: bool, result: dict[str, Any] | None = None, error: str = "",
               backoff_s: int = 60) -> str:
        """DONE, or re-QUEUED with back-off while attempts remain, else FAILED (escalation). Returns the new status."""
        j = self.get(jid)
        if ok:
            status, not_before = "DONE", None
        elif j["attempts"] < j["max_attempts"]:
            status, not_before = "QUEUED", _iso(_now() + timedelta(seconds=backoff_s * j["attempts"]))
        else:
            status, not_before = "FAILED", None
        self.conn.execute("UPDATE jobs SET status=?, not_before=?, finished_at=?, result=?, error=?, worker=NULL WHERE id=?",
                          (status, not_before, _iso(_now()) if status != "QUEUED" else None,
                           json.dumps(result or {}, default=str), error[-2000:] or None, jid))
        if j["worker"]:
            col = "jobs_done" if ok else "jobs_failed"
            self.conn.execute(f"UPDATE workers SET {col}={col}+1 WHERE id=?", (j["worker"],))
        return status

    def recover_stale(self, stale_after_s: int = 300) -> list[str]:
        """Jobs RUNNING whose heartbeat stopped (worker died): re-queue or fail them; mark dead workers."""
        cutoff = _iso(_now() - timedelta(seconds=stale_after_s))
        stale = [r["id"] for r in self.conn.execute("SELECT id FROM jobs WHERE status='RUNNING' AND heartbeat_at<?", (cutoff,))]
        for jid in stale:
            self.finish(jid, False, error=f"worker lost: no heartbeat for > {stale_after_s}s", backoff_s=0)
        self.conn.execute("UPDATE workers SET status='DEAD', current_job=NULL WHERE status<>'DEAD' AND status<>'STOPPED'"
                          " AND heartbeat_at<?", (cutoff,))
        return stale


def execute(q: Queue, wid: str, job: dict[str, Any], heartbeat_s: float = 10.0, log_dir: Path | None = None) -> str:
    """Run one claimed job in a subprocess with timeout and heartbeats. Returns the job's new status."""
    kind = KINDS[job["kind"]]
    argv = kind.build(json.loads(job["params"]), q.db)
    log_dir = log_dir or PROJECT_ROOT / "runs" / "jobs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / f"{job['id']}.attempt{job['attempts']}.log"
    q.conn.execute("UPDATE jobs SET log_path=? WHERE id=?", (str(log), job["id"]))
    q.worker_beat(wid, "RUNNING", job["id"])
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as fh:
        fh.write(" ".join(argv) + "\n")
        fh.flush()
        proc = subprocess.Popen(argv, cwd=PROJECT_ROOT, stdout=fh, stderr=subprocess.STDOUT)
        timed_out, last_beat = False, time.time()
        while proc.poll() is None:
            time.sleep(min(heartbeat_s, 1.0))
            if time.time() - t0 > job["timeout_s"]:
                proc.kill()
                proc.wait()
                timed_out = True
                break
            if time.time() - last_beat >= heartbeat_s:
                q.job_beat(job["id"])
                q.worker_beat(wid, "RUNNING", job["id"])
                last_beat = time.time()
    tail = log.read_text(encoding="utf-8", errors="replace")[-4000:]
    result = {"returncode": proc.returncode, "seconds": round(time.time() - t0, 1),
              "report": next((ln.split("report:", 1)[1].strip() for ln in tail.splitlines() if "report:" in ln), None),
              "verdict": next((ln.strip() for ln in tail.splitlines()
                               if ln.startswith(("NO EDGE", "EDGE FOUND", "INSUFFICIENT"))), None)}
    if timed_out:
        status = q.finish(job["id"], False, result, error=f"timeout after {job['timeout_s']}s\n{tail[-1500:]}")
    else:
        status = q.finish(job["id"], proc.returncode == 0, result, error="" if proc.returncode == 0 else tail[-1500:])
    q.worker_beat(wid, "IDLE", None)
    return status


def run_worker(db: str | Path, department: str | None = None, max_jobs: int | None = None, idle_exit_s: float = 0,
               poll_s: float = 5.0, heartbeat_s: float = 10.0, stale_after_s: int = 300,
               log: Callable[[str], None] = print) -> dict[str, int]:
    """Worker loop: recover stale jobs, claim, execute, repeat. Exits after ``max_jobs`` or ``idle_exit_s`` idle."""
    q = Queue(db)
    wid = q.register_worker(department)
    counts = {"done": 0, "failed": 0, "requeued": 0}
    idle_since = time.time()
    try:
        while max_jobs is None or sum(counts.values()) < max_jobs:
            for jid in q.recover_stale(stale_after_s):
                log(f"[{wid}] recovered stale job {jid}")
            job = q.claim(wid, department)
            if job is None:
                q.worker_beat(wid, "IDLE", None)
                if idle_exit_s and time.time() - idle_since >= idle_exit_s:
                    break
                time.sleep(poll_s)
                continue
            log(f"[{wid}] {job['id']} {job['kind']} {job['params']} (attempt {job['attempts']}/{job['max_attempts']})")
            status = execute(q, wid, job, heartbeat_s)
            counts["done" if status == "DONE" else "failed" if status == "FAILED" else "requeued"] += 1
            log(f"[{wid}] {job['id']} -> {status}")
            idle_since = time.time()
    finally:
        q.worker_beat(wid, "STOPPED", None)
        q.close()
    return counts


def lab_status(db: str | Path, stale_after_s: int = 300) -> dict[str, Any]:
    """Everything here is counted from the database: no estimated or decorative figures."""
    q = Queue(db)
    c = q.conn
    cutoff = _iso(_now() - timedelta(seconds=stale_after_s))
    jobs = {r[0]: r[1] for r in c.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")}
    by_dept = {f"{r[0]}:{r[1]}": r[2] for r in c.execute("SELECT department, status, COUNT(*) FROM jobs GROUP BY 1, 2")}
    workers = [dict(r) for r in c.execute("SELECT id, department, status, current_job, heartbeat_at, jobs_done, jobs_failed"
                                          " FROM workers WHERE heartbeat_at>=? AND status NOT IN ('STOPPED','DEAD')",
                                          (cutoff,))]
    running = [dict(r) for r in c.execute("SELECT id, kind, department, params, started_at, attempts FROM jobs"
                                          " WHERE status='RUNNING'")]

    def table(sql: str) -> dict[str, int]:
        try:
            return {str(r[0]): int(r[1]) for r in c.execute(sql)}
        except sqlite3.OperationalError:  # memory tables not created yet
            return {}
    out = {"as_of": _iso(_now()), "lab": "ONLINE" if workers else "OFFLINE (no live worker)",
           "active_agents": len(workers), "agents": workers, "running_jobs": running, "jobs": jobs, "jobs_by_department": by_dept,
           "research_runs": table("SELECT verdict, COUNT(*) FROM research_runs GROUP BY verdict"),
           "hypotheses": table("SELECT status, COUNT(*) FROM hypotheses GROUP BY status"),
           "strategies": table("SELECT status, COUNT(*) FROM strategies GROUP BY status"),
           "experiments": sum(table("SELECT 'n', COUNT(*) FROM experiments").values()),
           "preregistrations": table("SELECT COALESCE(verdict, 'PENDING'), COUNT(*) FROM preregistrations GROUP BY 1")}
    try:
        from xquant.lab.hq import strategy_hq
        from xquant.memory.store import ResearchMemory
        out["strategy_tiers"] = strategy_hq(ResearchMemory(db), top=0)["tiers"]
    except Exception as exc:  # status must never fail because of the HQ view
        out["strategy_tiers"] = f"unavailable: {type(exc).__name__}"
    q.close()
    return out
