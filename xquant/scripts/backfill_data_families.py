"""One-off migration (2026-10-08): key past multiple-testing trials and protected-split openings by underlying data.

Before this, trials were counted per config symbol (EURUSD_H1, EURUSD_H1_RV and EURUSD_H1_DXY share the same bars
but had separate counts) and the TEST/FINAL guard only lived inside one run. For every (asset, dataset_version) row
whose dataset can be rebuilt offline with the same version, its trial sums are added to FAMILY:bars:<sha>; past
TEST/FINAL openings are written to the protected-split ledger. Idempotent: refuses to run twice.
Usage: uv run python scripts/backfill_data_families.py
"""

import sys

from xquant.config import load_config
from xquant.data.engine import DataEngine
from xquant.data.schema import frame_sha256
from xquant.memory.store import ResearchMemory

mem = ResearchMemory("research_output/memory.db")
if mem.conn.execute("SELECT COUNT(*) FROM trials WHERE asset LIKE 'FAMILY:%'").fetchone()[0]:
    sys.exit("families already exist - backfill was done; refusing to double count")
rows = mem.conn.execute("SELECT asset, dataset_version, n, sum_sr, sum_sr2 FROM trials").fetchall()
keys: dict[str, str] = {}
skipped = []
for r in rows:
    asset, dv = r["asset"], r["dataset_version"]
    try:
        ds = DataEngine(load_config(asset).asset, offline=True).load()
    except Exception as exc:  # config gone or data not cached
        skipped.append((asset, dv, f"cannot load: {type(exc).__name__}"))
        continue
    if ds.version != dv:
        skipped.append((asset, dv, f"dataset version now {ds.version}"))
        continue
    key = f"bars:{ds.meta.sha256[:16]}"
    keys[asset] = key
    with mem.tx() as c:
        c.execute("INSERT INTO trials VALUES (?,?,?,?,?) ON CONFLICT(asset, dataset_version) DO UPDATE SET "
                  "n = n + excluded.n, sum_sr = sum_sr + excluded.sum_sr, sum_sr2 = sum_sr2 + excluded.sum_sr2",
                  (mem.family_key(key), "", r["n"], r["sum_sr"], r["sum_sr2"]))
    print(f"{asset:16s} {dv} n={r['n']:>7d} -> {key}")
# protected-split openings recorded so far (only day-trading runs opened TEST/FINAL)
for a in mem.conn.execute("SELECT run_id, split, who FROM split_access WHERE split IN ('test','final')").fetchall():
    run = mem.conn.execute("SELECT asset FROM research_runs WHERE id=?", (a["run_id"],)).fetchone()
    data_asset = {"DAYTRADE:NAS100": "NAS100_M1", "DAYTRADE:USA500": "USA500_M1"}.get(run["asset"], run["asset"])
    bars, _, _ = DataEngine(load_config(data_asset).asset, offline=True).load_bars()
    key = f"bars:{frame_sha256(bars)[:16]}"
    mem.ledger_open(key, a["split"], a["run_id"], a["who"])
    print(f"ledger: {a['run_id']} opened {a['split']} of {data_asset} ({key})")
for s in skipped:
    print("SKIPPED", *s)
for fam in mem.conn.execute("SELECT asset, n FROM trials WHERE asset LIKE 'FAMILY:%'").fetchall():
    print("family", fam["asset"], fam["n"], "<-", sorted(a for a, k in keys.items() if mem.family_key(k) == fam["asset"]))
