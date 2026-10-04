"""Command-line interface.

    xquant data validate --asset EURUSD [--offline]
    xquant research --asset EURUSD --mode quick|standard|deep [--offline] [--seed N]
    xquant dashboard [--serve --port 8765]
    xquant memory runs|experiments|hypotheses|strategies [--limit N]
    xquant sources

There is deliberately no command that places orders: X-QUANT is research / backtest / paper only.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from xquant.config import PROJECT_ROOT, load_config
from xquant.errors import XQuantError
from xquant.logging_utils import setup_logging


def _overrides(args: argparse.Namespace) -> dict[str, Any]:
    o: dict[str, Any] = {"research": {}}
    if getattr(args, "mode", None):
        o["research"]["mode"] = args.mode
    if getattr(args, "seed", None) is not None:
        o["research"]["seed"] = args.seed
    if getattr(args, "memory", None):
        o["research"]["memory_path"] = args.memory
    if getattr(args, "min_trades_per_day", None):
        o.setdefault("stats", {})["min_trades_per_day"] = args.min_trades_per_day
    if getattr(args, "focus", None):
        o.setdefault("stats", {})["focus"] = args.focus
    if getattr(args, "max_minutes", None):
        mode = getattr(args, "mode", None) or "standard"
        o["budgets"] = {mode: {"max_compute_minutes": args.max_minutes}}
    return o


def cmd_data(args: argparse.Namespace) -> int:
    from xquant.data.engine import DataEngine
    cfg = load_config(args.asset, _overrides(args))
    ds = DataEngine(cfg.asset, offline=args.offline).load()
    print(json.dumps({"summary": ds.summary(), "quality": ds.quality.to_dict(), "notes": ds.meta.notes,
                      "exogenous": {k: {kk: v.get(kk) for kk in ("status", "coverage", "lag_days", "reason")}
                                    for k, v in ds.exog_meta.items()}}, indent=2, default=str))
    return 0 if ds.quality.verdict != "FAIL" else 2


def cmd_research(args: argparse.Namespace) -> int:
    from xquant.dashboard.render import render_dashboard
    from xquant.memory.store import ResearchMemory
    from xquant.report.builder import write_report
    from xquant.research.orchestrator import ResearchOrchestrator
    cfg = load_config(args.asset, _overrides(args))
    setup_logging(args.log_level, PROJECT_ROOT / cfg.research.runs_dir / "xquant.log.jsonl")
    mem = ResearchMemory(cfg.research.memory_path)
    out = ResearchOrchestrator(cfg, offline=args.offline, memory=mem).run()
    md, js = write_report(out)
    mem.update_run(out.run_id, report_path=str(md.relative_to(PROJECT_ROOT)))
    dash = render_dashboard(mem)
    print(f"\n{out.verdict}: {out.verdict_detail}\nreport: {md}\njson:   {js}\ndashboard: {dash}")
    return 0


def cmd_confirm(args: argparse.Namespace) -> int:
    from xquant.dashboard.render import render_dashboard
    from xquant.memory.store import ResearchMemory
    from xquant.report.builder import write_report
    from xquant.research.confirm import ConfirmatoryStudy, load_spec, summarise
    spec = load_spec(args.spec)
    cfg = load_config(spec["asset"], _overrides(args))
    setup_logging(args.log_level, PROJECT_ROOT / cfg.research.runs_dir / "xquant.log.jsonl")
    mem = ResearchMemory(cfg.research.memory_path)
    out = ConfirmatoryStudy(cfg, spec, offline=args.offline, memory=mem).run()
    md, js = write_report(out)
    mem.update_run(out.run_id, report_path=str(md.relative_to(PROJECT_ROOT)))
    dash = render_dashboard(mem)
    print(f"\n{summarise(out)}\n\n{out.verdict}: {out.verdict_detail}\nreport: {md}\njson:   {js}\ndashboard: {dash}")
    return 0


def cmd_allocate(args: argparse.Namespace) -> int:
    from xquant.allocation.study import AllocationStudy, load_spec, write_report
    from xquant.dashboard.render import render_dashboard
    from xquant.memory.store import ResearchMemory
    cfg = load_config("EURUSD", _overrides(args))
    setup_logging(args.log_level, PROJECT_ROOT / cfg.research.runs_dir / "xquant.log.jsonl")
    mem = ResearchMemory(cfg.research.memory_path)
    out = AllocationStudy(load_spec(args.spec), mem, offline=args.offline).run()
    md, js = write_report(out)
    mem.update_run(out["run_id"], report_path=str(md.relative_to(PROJECT_ROOT)))
    render_dashboard(mem)
    for r in out["results"]:
        p = r["primary"]
        print(f"{r['variant']}: {r['status']} | primary Sharpe {p.get('sharpe', float('nan')):.2f} "
              f"(gross {r['gross_primary_sharpe']:.2f}), CAGR {p.get('ann_return', float('nan')):.2%}, "
              f"max DD {p.get('max_drawdown', float('nan')):.2%} | checks {r['checks']}")
    print(f"\n{out['verdict']}\nreport: {md}")
    return 0


def cmd_portfolio(args: argparse.Namespace) -> int:
    from xquant.memory.store import ResearchMemory
    from xquant.portfolio import format_view, portfolio_view
    cfg = load_config("EURUSD", _overrides(args))
    print(format_view(portfolio_view(ResearchMemory(cfg.research.memory_path), args.min_trades_per_day)))
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    from xquant.dashboard.render import render_dashboard, serve
    from xquant.memory.store import ResearchMemory
    path = args.memory or "research_output/memory.db"
    if args.serve:
        serve(path, args.port)
        return 0
    print(render_dashboard(ResearchMemory(path)))
    return 0


def cmd_memory(args: argparse.Namespace) -> int:
    from xquant.memory.store import ResearchMemory
    mem = ResearchMemory(args.memory or "research_output/memory.db")
    if args.what == "compact":
        print(json.dumps(mem.compact(archive=PROJECT_ROOT / "research_output" / "archive" / "hypotheses_rejected.jsonl.gz")))
        for p in sorted((PROJECT_ROOT / "research_output" / "reports").glob("*.json")):
            data = json.loads(p.read_text())
            for key in ("dossiers", "ranking"):
                for d in data.get(key, []):
                    eq = d.get("equity") or {}
                    n = len(eq.get("combined") or [])
                    if n > 400:
                        d["equity"] = {k: v[:: n // 400] for k, v in eq.items()}
            p.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        return 0
    q = {"runs": "SELECT id, asset, mode, status, verdict, started_at FROM research_runs ORDER BY started_at DESC",
         "experiments": "SELECT id, run_id, kind, line, status, conclusion FROM experiments ORDER BY id DESC",
         "hypotheses": "SELECT id, status, round(p_value, 6) AS p, round(q_value, 4) AS q, sample, description FROM hypotheses "
                       "ORDER BY p_value",
         "strategies": "SELECT id, status, round(score, 3) AS score, description, reasons FROM strategies ORDER BY score DESC"}[args.what]
    for row in mem.query(q + f" LIMIT {int(args.limit)}"):
        print(json.dumps(row, default=str))
    return 0


def cmd_sources(_: argparse.Namespace) -> int:
    from xquant.data.sources.base import registered_kinds
    print("\n".join(registered_kinds()))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="xquant", description="X-QUANT research laboratory (no live trading)")
    p.add_argument("--log-level", default="INFO")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("data", help="load and validate data")
    d.add_argument("action", choices=["validate"])
    d.add_argument("--asset", required=True)
    d.add_argument("--offline", action="store_true", help="use pinned snapshots in datasets/")
    d.set_defaults(fn=cmd_data)
    r = sub.add_parser("research", help="run an autonomous research cycle")
    r.add_argument("--asset", required=True)
    r.add_argument("--mode", choices=["quick", "standard", "deep"])
    r.add_argument("--seed", type=int)
    r.add_argument("--memory")
    r.add_argument("--offline", action="store_true")
    r.add_argument("--max-minutes", type=float, help="override the mode's compute budget (stops gracefully)")
    r.add_argument("--min-trades-per-day", type=float, help="require at least this trading frequency")
    r.add_argument("--focus", nargs="+", help="feature-name substrings to test first (e.g. x_px_dxy)")
    r.set_defaults(fn=cmd_research)
    cf = sub.add_parser("confirm", help="run a pre-registered (confirmatory) hypothesis test once")
    cf.add_argument("--spec", required=True, help="pre-registration YAML (configs/preregistered/*.yaml)")
    cf.add_argument("--offline", action="store_true", help="use cached/snapshotted data only")
    cf.add_argument("--memory", help="research memory path")
    cf.set_defaults(fn=cmd_confirm)
    al = sub.add_parser("allocate", help="run a pre-registered allocation (portfolio / sizing) study once")
    al.add_argument("--spec", required=True, help="allocation pre-registration YAML")
    al.add_argument("--offline", action="store_true", help="use cached data only")
    al.add_argument("--memory", help="research memory path")
    al.set_defaults(fn=cmd_allocate)
    pf = sub.add_parser("portfolio", help="combine validated strategies; frequency measured at portfolio level")
    pf.add_argument("--min-trades-per-day", type=float, default=1.0, help="portfolio-level frequency requirement")
    pf.add_argument("--memory", help="research memory path")
    pf.set_defaults(fn=cmd_portfolio)
    db = sub.add_parser("dashboard", help="render or serve the dashboard")
    db.add_argument("--serve", action="store_true")
    db.add_argument("--port", type=int, default=8765)
    db.add_argument("--memory")
    db.set_defaults(fn=cmd_dashboard)
    m = sub.add_parser("memory", help="inspect research memory")
    m.add_argument("what", choices=["runs", "experiments", "hypotheses", "strategies", "compact"])
    m.add_argument("--limit", type=int, default=20)
    m.add_argument("--memory")
    m.set_defaults(fn=cmd_memory)
    s = sub.add_parser("sources", help="list registered data source kinds")
    s.set_defaults(fn=cmd_sources)
    args = p.parse_args(argv)
    setup_logging(args.log_level)
    try:
        return int(args.fn(args))
    except XQuantError as exc:
        print(f"X-QUANT error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
