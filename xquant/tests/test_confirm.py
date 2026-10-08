"""Confirmatory (pre-registered) mode: controls and the no-editing / contamination rules."""

import numpy as np
import pandas as pd
import pytest

from tests.conftest import synthetic_dataset
from tests.test_integration import _cfg, _edge_returns
from xquant.errors import ConfigError
from xquant.memory.store import ResearchMemory
from xquant.report.builder import build_markdown
from xquant.research.confirm import ConfirmatoryStudy, spec_sha256


def _spec(name="ret5_reversal", feature="ret_5"):
    return {"name": name, "asset": "SYN", "hypothesis": "after a sharp 5-bar drop the price drifts up",
            "variants": [{"conditions": [{"feature": feature, "side": "low", "q": 0.1}], "direction": 1, "hold": h}
                         for h in (3, 5)]}


@pytest.mark.slow
def test_positive_control_preregistered_edge_is_confirmed(tmp_path):
    ds = synthetic_dataset(_edge_returns(5000, seed=5))
    cfg = _cfg(ds, tmp_path)
    mem = ResearchMemory(cfg.research.memory_path)
    out = ConfirmatoryStudy(cfg, _spec(), memory=mem, dataset=ds).run()
    assert out.preregistration["multiple_testing_n"] == 2  # only the registered variants count
    assert not out.preregistration["contaminated_features"]
    assert out.verdict.startswith("EDGE FOUND"), [(d["status"], d["reasons"][:3]) for d in out.dossiers]
    md = build_markdown(out)
    assert "Pre-registered hypothesis" in md and spec_sha256(_spec()) in md and "Feature discovery" not in md
    # a confirmatory test runs once, and a registered spec cannot be edited
    with pytest.raises(ConfigError, match="runs once"):
        ConfirmatoryStudy(cfg, _spec(), memory=mem, dataset=ds).run()
    edited = _spec()
    edited["variants"][0]["hold"] = 4
    with pytest.raises(ConfigError, match="cannot be edited"):
        ConfirmatoryStudy(cfg, edited, memory=mem, dataset=ds).run()


@pytest.mark.slow
def test_negative_control_random_walk_is_not_confirmed(tmp_path):
    ds = synthetic_dataset(np.random.default_rng(99).normal(0, 0.006, 5000))
    cfg = _cfg(ds, tmp_path)
    out = ConfirmatoryStudy(cfg, _spec(), memory=ResearchMemory(cfg.research.memory_path), dataset=ds).run()
    assert out.verdict == "NO EDGE FOUND", out.verdict_detail
    assert not any(d["status"] == "ROBUST" for d in out.dossiers)


def test_contaminated_feature_pays_the_exploratory_penalty(tmp_path):
    ds = synthetic_dataset(np.random.default_rng(7).normal(0, 0.006, 3000))
    cfg = _cfg(ds, tmp_path)
    mem = ResearchMemory(cfg.research.memory_path)
    # exploratory research already used ret_5 (any asset) and ran many backtests on this dataset
    mem.conn.execute("INSERT INTO hypotheses (id, signature, asset, dataset_version, variables, status) "
                     "VALUES ('HYP-X', 'x', 'OTHER', 'v', '{\"feature\": \"ret_5\"}', 'REJECTED')")
    mem.conn.commit()
    mem.add_trials("SYN", ds.version, list(np.linspace(-1, 1, 500)))
    out = ConfirmatoryStudy(cfg, _spec("contaminated"), memory=mem, dataset=ds).run()
    assert out.preregistration["contaminated_features"] == {"ret_5": {"hypotheses:OTHER": 1}}
    assert out.preregistration["multiple_testing_n"] == 500 + 2
    assert out.trials["family"] == "exploratory"


def test_spec_must_match_config_asset(tmp_path):
    ds = synthetic_dataset(np.random.default_rng(1).normal(0, 0.006, 600))
    spec = _spec()
    spec["asset"] = "EURUSD_H1"
    with pytest.raises(ConfigError, match="registered for"):
        ConfirmatoryStudy(_cfg(ds, tmp_path), spec)


def test_portfolio_only_uses_validated_strategies(tmp_path):
    from xquant.memory.store import pack
    from xquant.portfolio import portfolio_view
    mem = ResearchMemory(tmp_path / "m.db")
    assert portfolio_view(mem, 1.0)["verdict"].startswith("NO PORTFOLIO")
    dates = [str(d.date()) for d in pd.date_range("2020-01-01", periods=50, freq="7D")]
    rng = np.random.default_rng(0)
    for i, status in enumerate(["ROBUST", "ROBUST", "REJECTED"]):
        eq = list(np.cumsum(rng.normal(0.002, 0.01, 50)))
        dossier = {"validation": {"trades": 252, "years": 2.0, "sharpe": 1.0}, "equity": {"dates": dates, "combined": eq}}
        mem.conn.execute("INSERT INTO strategies (id, signature, asset, dataset_version, status, description, dossier) "
                         "VALUES (?,?,?,?,?,?,?)", (f"S{i}", f"g{i}", "A", "v", status, "rule", pack(dossier)))
    mem.conn.commit()
    v = portfolio_view(mem, 1.0)
    assert [c["id"] for c in v["components"]] == ["S0", "S1"]  # the rejected one is never combined
    assert v["portfolio_trades_per_day"] == 1.0 and "below" not in v["verdict"]
    assert "approx_portfolio_sharpe" in v and set(v["correlation"]) == {"S0", "S1"}


def test_protected_split_ledger_and_data_families(tmp_path):
    from xquant.validation.splits import SplitGuard, reuse_tag
    mem = ResearchMemory(tmp_path / "m.db")
    g1 = SplitGuard(ledger=lambda k, s, w: mem.ledger_open(k, s, "RUN-1", w), data_key="bars:abc")
    g1.request("final", "evaluate", "a")
    assert g1.prior_opens["final"] == 0 and reuse_tag(g1, "EDGE FOUND (provisional)") == "EDGE FOUND (provisional)"
    g2 = SplitGuard(ledger=lambda k, s, w: mem.ledger_open(k, s, "RUN-2", w), data_key="bars:abc")
    g2.request("final", "evaluate", "b")  # another run, same underlying data (e.g. another config of the same bars)
    assert g2.prior_opens["final"] == 1 and "not clean OOS" in reuse_tag(g2, "EDGE FOUND (provisional)")
    assert reuse_tag(g2, "NO EDGE FOUND") == "NO EDGE FOUND"
    # two configs of the same bars share one multiple-testing family
    mem.add_trials("EURUSD_H1", "v1", [0.1] * 300)
    mem.add_trials_family("bars:abc", [0.1] * 300)
    mem.add_trials("EURUSD_H1_RV", "v2", [0.2] * 50)
    mem.add_trials_family("bars:abc", [0.2] * 50)
    assert mem.trials_for("EURUSD_H1_RV", "v2", "bars:abc")[0] == 350
    assert mem.trials_for("EURUSD_H1", "v1", "")[0] == 300
