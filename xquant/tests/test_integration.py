"""End-to-end controls of the whole laboratory.

Negative control: on a pure random walk the lab must conclude NO EDGE FOUND.
Positive control: with a known, tradeable effect injected, the lab must find it and it must survive.
Synthetic data is used only here, to calibrate the lab itself.
"""

import numpy as np
import pytest

from tests.conftest import synthetic_dataset
from xquant.config import load_config
from xquant.memory.store import ResearchMemory
from xquant.report.builder import build_markdown
from xquant.research.orchestrator import ResearchOrchestrator


def _cfg(ds, tmp_path):
    idx = ds.bars.index
    n = len(idx)
    return load_config("EURUSD", overrides={
        "research": {"mode": "quick", "seed": 3, "memory_path": str(tmp_path / "mem.db")},
        "asset": {"symbol": "SYN", "macro": [], "cross_assets": [],
                  "splits": {"train_end": str(idx[int(n * 0.55)].date()), "validation_end": str(idx[int(n * 0.72)].date()),
                             "test_end": str(idx[int(n * 0.86)].date()), "embargo_bars": 20}},
        "budgets": {"quick": {"max_experiments": 30, "max_generations": 6, "population": 40, "max_compute_minutes": 8,
                              "max_strategies": 6, "max_complexity": 3, "max_features": 60, "max_hypotheses": 1500,
                              "patience": 2, "max_line_failures": 1}},
        "robustness": {"random_entry_reps": 150, "mc_reps": 300},
    })


def _edge_returns(n: int, seed: int) -> np.ndarray:
    """Injected effect: after the 5-bar return falls into roughly its bottom 10%, the next 5 bars drift up."""
    rng = np.random.default_rng(seed)
    sigma = 0.006
    e = rng.normal(0, sigma, n)
    r = np.zeros(n)
    drift_left = 0
    for t in range(n):
        r[t] = e[t] + (0.3 * sigma if drift_left > 0 else 0.0)
        drift_left = max(0, drift_left - 1)
        if t >= 5 and r[t - 4:t + 1].sum() < -1.28 * sigma * np.sqrt(5) and drift_left == 0:
            drift_left = 5
    return r


@pytest.mark.slow
def test_negative_control_random_walk_gives_no_edge(tmp_path):
    ds = synthetic_dataset(np.random.default_rng(99).normal(0, 0.006, 5000))
    cfg = _cfg(ds, tmp_path)
    mem = ResearchMemory(cfg.research.memory_path)
    out = ResearchOrchestrator(cfg, memory=mem, dataset=ds).run()
    assert out.verdict == "NO EDGE FOUND", out.verdict_detail
    assert not any(d["status"] == "ROBUST" for d in out.dossiers)
    md = build_markdown(out)
    assert "NO EDGE FOUND" in md and "Limitations" in md
    # memory: a second run must not re-discover hypotheses on the same data
    out2 = ResearchOrchestrator(cfg, memory=mem, dataset=ds).run()
    assert out2.hypotheses["new"] == 0 and out2.hypotheses["reused"] > 0
    runs = mem.query("SELECT id FROM research_runs")
    assert len(runs) == 2
    access = mem.query("SELECT split, purpose FROM split_access WHERE split IN ('test', 'final')")
    assert all(a["purpose"] == "evaluate" for a in access)


@pytest.mark.slow
def test_positive_control_injected_edge_is_found_and_survives(tmp_path):
    ds = synthetic_dataset(_edge_returns(5000, seed=5))
    cfg = _cfg(ds, tmp_path)
    out = ResearchOrchestrator(cfg, memory=ResearchMemory(cfg.research.memory_path), dataset=ds).run()
    assert out.hypotheses["validated"], "the injected condition should be a validated hypothesis"
    feats = {h["feature"] for h in out.hypotheses["validated"]}
    assert feats & {"ret_5", "ret_3", "ret_10", "zdist_10", "fromhigh_20", "zdist_20", "ret_2"}, feats
    robust = [d for d in out.dossiers if d["status"] == "ROBUST"]
    assert robust, [(d["status"], d["reasons"][:2]) for d in out.dossiers]
    assert out.verdict.startswith("EDGE FOUND"), out.verdict_detail
    assert robust[0]["genome"]["direction"] == 1
