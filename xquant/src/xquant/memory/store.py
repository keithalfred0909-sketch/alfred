"""RESEARCH MEMORY and EXPERIMENT TRACKER (SQLite, single file, append-mostly).

* Every experiment gets an ID (EXP-0000001) with dataset version, code version, config fingerprint,
  seed, parameters, metrics and conclusion -> reproducible.
* Hypotheses and strategies are keyed by (signature, dataset_version). Before testing anything the
  engines ask ``known_hypothesis`` / ``known_strategy``: if it was already tested on the same data it
  is NOT re-discovered; its stored verdict is reused. New data (new dataset version) re-opens it.
* Trial counts per asset/dataset accumulate across runs so the deflated Sharpe ratio accounts for the
  whole research history, not just the current run.
"""

from __future__ import annotations

import json
import math
import sqlite3
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from xquant.config import PROJECT_ROOT

SCHEMA = """
CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS research_runs (
  id TEXT PRIMARY KEY, asset TEXT, mode TEXT, started_at TEXT, finished_at TEXT, status TEXT,
  verdict TEXT, dataset_version TEXT, code_version TEXT, config_fingerprint TEXT, seed INTEGER,
  progress TEXT, summary TEXT, report_path TEXT);
CREATE TABLE IF NOT EXISTS experiments (
  id TEXT PRIMARY KEY, run_id TEXT, created_at TEXT, kind TEXT, line TEXT, asset TEXT,
  dataset_version TEXT, code_version TEXT, config_fingerprint TEXT, seed INTEGER,
  params TEXT, metrics TEXT, conclusion TEXT, status TEXT, duration_s REAL);
CREATE TABLE IF NOT EXISTS hypotheses (
  id TEXT PRIMARY KEY, signature TEXT, asset TEXT, dataset_version TEXT, experiment_id TEXT,
  description TEXT, variables TEXT, period TEXT, sample INTEGER, baseline REAL, result REAL,
  p_value REAL, q_value REAL, effect_size REAL, confidence REAL, complexity INTEGER, status TEXT,
  data TEXT, created_at TEXT, UNIQUE(signature, asset, dataset_version));
CREATE TABLE IF NOT EXISTS strategies (
  id TEXT PRIMARY KEY, signature TEXT, asset TEXT, dataset_version TEXT, experiment_id TEXT, run_id TEXT,
  description TEXT, genome TEXT, status TEXT, reasons TEXT, score REAL, dossier TEXT, created_at TEXT,
  UNIQUE(signature, asset, dataset_version));
CREATE TABLE IF NOT EXISTS findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, experiment_id TEXT, asset TEXT, dataset_version TEXT,
  engine TEXT, category TEXT, name TEXT, status TEXT, data TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS research_lines (
  run_id TEXT, name TEXT, status TEXT, experiments INTEGER, failures INTEGER, stop_reason TEXT,
  best_score REAL, updated_at TEXT, PRIMARY KEY(run_id, name));
CREATE TABLE IF NOT EXISTS split_access (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, split TEXT, purpose TEXT, who TEXT, at TEXT);
CREATE TABLE IF NOT EXISTS trials (
  asset TEXT, dataset_version TEXT, n INTEGER, sum_sr REAL, sum_sr2 REAL, PRIMARY KEY(asset, dataset_version));
CREATE TABLE IF NOT EXISTS log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, at TEXT, level TEXT, message TEXT);
"""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def code_version() -> str:
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT, capture_output=True,
                             text=True, timeout=5).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "src"], cwd=PROJECT_ROOT, capture_output=True,
                               text=True, timeout=5).stdout.strip()
        return f"{sha}{'-dirty' if dirty else ''}" if sha else "unknown"
    except Exception:
        return "unknown"


def _j(x: Any) -> str:
    def default(o: Any) -> Any:
        if hasattr(o, "item"):
            return o.item()
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return str(o)

    def clean(v: Any) -> Any:
        if isinstance(v, float) and not math.isfinite(v):
            return None
        if isinstance(v, dict):
            return {str(k): clean(w) for k, w in v.items()}
        if isinstance(v, list | tuple):
            return [clean(w) for w in v]
        return v
    return json.dumps(clean(x), default=default)


class ResearchMemory:
    def __init__(self, path: str | Path) -> None:
        p = Path(path)
        self.path = p if p.is_absolute() else PROJECT_ROOT / p
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def next_id(self, prefix: str, width: int) -> str:
        with self.tx() as c:
            c.execute("INSERT INTO counters(name, value) VALUES (?, 1) ON CONFLICT(name) DO UPDATE SET value = value + 1",
                      (prefix,))
            v = c.execute("SELECT value FROM counters WHERE name = ?", (prefix,)).fetchone()[0]
        return f"{prefix}-{v:0{width}d}"

    # ---- runs / experiments ----------------------------------------------------------------------
    def start_run(self, asset: str, mode: str, dataset_version: str, config_fp: str, seed: int) -> str:
        rid = self.next_id("RUN", 5)
        with self.tx() as c:
            c.execute("INSERT INTO research_runs(id, asset, mode, started_at, status, dataset_version, code_version,"
                      " config_fingerprint, seed, progress) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (rid, asset, mode, now(), "RUNNING", dataset_version, code_version(), config_fp, seed, "{}"))
        return rid

    def update_run(self, run_id: str, **fields: Any) -> None:
        sets, vals = [], []
        for k, v in fields.items():
            sets.append(f"{k} = ?")
            vals.append(_j(v) if isinstance(v, dict | list) else v)
        with self.tx() as c:
            c.execute(f"UPDATE research_runs SET {', '.join(sets)} WHERE id = ?", (*vals, run_id))

    def record_experiment(self, run_id: str, kind: str, line: str, asset: str, dataset_version: str,
                          config_fp: str, seed: int, params: dict[str, Any], metrics: dict[str, Any],
                          conclusion: str, status: str, duration_s: float) -> str:
        eid = self.next_id("EXP", 7)
        with self.tx() as c:
            c.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (eid, run_id, now(), kind, line, asset, dataset_version, code_version(), config_fp, seed,
                       _j(params), _j(metrics), conclusion, status, duration_s))
        return eid

    def log(self, run_id: str, message: str, level: str = "INFO") -> None:
        with self.tx() as c:
            c.execute("INSERT INTO log(run_id, at, level, message) VALUES (?,?,?,?)", (run_id, now(), level, message))

    def record_split_access(self, run_id: str, entries: list[dict[str, str]]) -> None:
        with self.tx() as c:
            c.executemany("INSERT INTO split_access(run_id, split, purpose, who, at) VALUES (?,?,?,?,?)",
                          [(run_id, e["split"], e["purpose"], e["who"], e["at"]) for e in entries])

    def set_line(self, run_id: str, name: str, status: str, experiments: int, failures: int,
                 stop_reason: str = "", best_score: float | None = None) -> None:
        with self.tx() as c:
            c.execute("INSERT INTO research_lines VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(run_id, name) DO UPDATE SET "
                      "status=excluded.status, experiments=excluded.experiments, failures=excluded.failures, "
                      "stop_reason=excluded.stop_reason, best_score=excluded.best_score, updated_at=excluded.updated_at",
                      (run_id, name, status, experiments, failures, stop_reason, best_score, now()))

    # ---- findings / hypotheses / strategies --------------------------------------------------------
    def record_findings(self, run_id: str, exp_id: str, asset: str, dv: str, findings: list[dict[str, Any]]) -> None:
        with self.tx() as c:
            c.executemany("INSERT INTO findings(run_id, experiment_id, asset, dataset_version, engine, category, name,"
                          " status, data, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          [(run_id, exp_id, asset, dv, f["engine"], f["category"], f["name"], f["status"], _j(f), now())
                           for f in findings])

    def known_hypotheses(self, asset: str, dv: str) -> dict[str, dict[str, Any]]:
        rows = self.conn.execute("SELECT signature, id, status, data FROM hypotheses WHERE asset=? AND dataset_version=?",
                                 (asset, dv)).fetchall()
        return {r["signature"]: {"id": r["id"], "status": r["status"], "data": json.loads(r["data"])} for r in rows}

    def record_hypotheses(self, asset: str, dv: str, exp_id: str, hyps: list[dict[str, Any]]) -> list[str]:
        ids = []
        with self.tx() as c:
            for h in hyps:
                row = c.execute("SELECT id FROM hypotheses WHERE signature=? AND asset=? AND dataset_version=?",
                                (h["signature"], asset, dv)).fetchone()
                if row:
                    ids.append(row["id"])
                    continue
                v = c.execute("INSERT INTO counters(name, value) VALUES ('HYP', 1) ON CONFLICT(name) DO UPDATE "
                              "SET value = value + 1 RETURNING value").fetchone()[0]
                hid = f"HYP-{v:06d}"
                c.execute("INSERT INTO hypotheses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (hid, h["signature"], asset, dv, exp_id, h["description"],
                           _j({"feature": h["feature"], "side": h["side"], "q": h["q"], "horizon": h["horizon"],
                               "regime": h["regime"]}), h["period"], h["sample"], h["baseline"], h["result"],
                           h["p_value"], h["q_value"], h["effect_size"], h["confidence"], h["complexity"], h["status"],
                           _j(h), now()))
                ids.append(hid)
        return ids

    def update_hypothesis_status(self, hid: str, status: str) -> None:
        with self.tx() as c:
            c.execute("UPDATE hypotheses SET status=? WHERE id=?", (status, hid))

    def known_strategy(self, signature: str, asset: str, dv: str) -> dict[str, Any] | None:
        r = self.conn.execute("SELECT id, status, reasons, score, dossier FROM strategies WHERE signature=? AND asset=?"
                              " AND dataset_version=?", (signature, asset, dv)).fetchone()
        if not r:
            return None
        return {"id": r["id"], "status": r["status"], "reasons": json.loads(r["reasons"] or "[]"), "score": r["score"],
                "dossier": json.loads(r["dossier"] or "{}")}

    def record_strategy(self, run_id: str, exp_id: str, asset: str, dv: str, dossier: dict[str, Any]) -> str:
        sig = dossier["genome_signature"]
        existing = self.known_strategy(sig, asset, dv)
        with self.tx() as c:
            if existing:
                c.execute("UPDATE strategies SET status=?, reasons=?, score=?, dossier=? WHERE id=?",
                          (dossier["status"], _j(dossier["reasons"]), dossier.get("score"), _j(dossier), existing["id"]))
                return str(existing["id"])
            v = c.execute("INSERT INTO counters(name, value) VALUES ('STR', 1) ON CONFLICT(name) DO UPDATE "
                          "SET value = value + 1 RETURNING value").fetchone()[0]
            sid = f"STR-{v:06d}"
            c.execute("INSERT INTO strategies VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (sid, sig, asset, dv, exp_id, run_id, dossier["description"], _j(dossier["genome"]),
                       dossier["status"], _j(dossier["reasons"]), dossier.get("score"), _j(dossier), now()))
        return sid

    # ---- trials ----------------------------------------------------------------------------------
    def add_trials(self, asset: str, dv: str, srs: list[float]) -> tuple[int, float]:
        s = [x for x in srs if math.isfinite(x)]
        with self.tx() as c:
            c.execute("INSERT INTO trials VALUES (?,?,?,?,?) ON CONFLICT(asset, dataset_version) DO UPDATE SET "
                      "n = n + excluded.n, sum_sr = sum_sr + excluded.sum_sr, sum_sr2 = sum_sr2 + excluded.sum_sr2",
                      (asset, dv, len(s), sum(s), sum(x * x for x in s)))
        return self.trials(asset, dv)

    def trials(self, asset: str, dv: str) -> tuple[int, float]:
        r = self.conn.execute("SELECT n, sum_sr, sum_sr2 FROM trials WHERE asset=? AND dataset_version=?",
                              (asset, dv)).fetchone()
        if not r or r["n"] < 2:
            return (int(r["n"]) if r else 0, 0.0)
        n, s, s2 = r["n"], r["sum_sr"], r["sum_sr2"]
        return int(n), float(max(s2 / n - (s / n) ** 2, 0.0))

    # ---- maintenance -----------------------------------------------------------------------------
    def compact(self, max_points: int = 400) -> dict[str, int]:
        """Downsample stored equity curves to ``max_points`` and VACUUM. Verdicts and metrics untouched."""
        changed = 0
        rows = self.conn.execute("SELECT id, dossier FROM strategies").fetchall()
        with self.tx() as c:
            for r in rows:
                d = json.loads(r["dossier"] or "{}")
                eq = d.get("equity") or {}
                n = len(eq.get("combined") or [])
                if n > max_points:
                    step = n // max_points
                    d["equity"] = {k: v[::step] for k, v in eq.items()}
                    c.execute("UPDATE strategies SET dossier=? WHERE id=?", (_j(d), r["id"]))
                    changed += 1
        before = self.path.stat().st_size
        self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self.conn.execute("VACUUM")
        return {"strategies_downsampled": changed, "bytes_before": before, "bytes_after": self.path.stat().st_size}

    # ---- queries for dashboard / CLI ---------------------------------------------------------------
    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def counts(self, run_id: str | None = None) -> dict[str, int]:
        w, p = ("WHERE run_id = ?", (run_id,)) if run_id else ("", ())
        out = {"experiments": self.conn.execute(f"SELECT COUNT(*) FROM experiments {w}", p).fetchone()[0],
               "hypotheses": self.conn.execute("SELECT COUNT(*) FROM hypotheses").fetchone()[0]}
        for status in ["REJECTED", "OVERFIT", "PASSED_SELECTION", "ROBUST", "UNVALIDATED"]:
            out[f"strategies_{status.lower()}"] = self.conn.execute(
                f"SELECT COUNT(*) FROM strategies WHERE status = ? {'AND run_id = ?' if run_id else ''}",
                (status, *p)).fetchone()[0]
        out["strategies"] = self.conn.execute(f"SELECT COUNT(*) FROM strategies {w}", p).fetchone()[0]
        for status in ["VALIDATION", "REJECTED", "OVERFIT", "ROBUST", "DEAD"]:
            out[f"hypotheses_{status.lower()}"] = self.conn.execute(
                "SELECT COUNT(*) FROM hypotheses WHERE status = ?", (status,)).fetchone()[0]
        return out
