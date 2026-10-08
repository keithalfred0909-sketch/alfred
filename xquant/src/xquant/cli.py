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


def cmd_daytrade(args: argparse.Namespace) -> int:
    from xquant.dashboard.render import render_dashboard
    from xquant.daytrade.study import DayTradeStudy, load_spec, write_report
    from xquant.memory.store import ResearchMemory
    cfg = load_config("NAS100_M1", _overrides(args))
    setup_logging(args.log_level, PROJECT_ROOT / cfg.research.runs_dir / "xquant.log.jsonl")
    mem = ResearchMemory(cfg.research.memory_path)
    out = DayTradeStudy(load_spec(args.spec), mem, offline=args.offline).run()
    md, js = write_report(out)
    mem.update_run(out["run_id"], report_path=str(md.relative_to(PROJECT_ROOT)))
    render_dashboard(mem)
    for r in out["results"]:
        p = r["primary"]
        print(f"variant {r['variant']}: {r['status']} | {p.get('trades')} trades, mean R {p.get('mean_r', float('nan')):.3f} "
              f"CI {p.get('mean_r_ci')}, win {p.get('win_rate', float('nan')):.1%}, CAGR@1% {p.get('cagr_at_1pct_risk', float('nan')):.2%} "
              f"| checks {r['checks']}")
    print(f"\n{out['verdict']}\nreport: {md}")
    return 0


def cmd_ml(args: argparse.Namespace) -> int:
    from xquant.dashboard.render import render_dashboard
    from xquant.memory.store import ResearchMemory
    from xquant.ml.walkforward import MLStudy, load_spec, write_report
    cfg = load_config("EURUSD", _overrides(args))
    setup_logging(args.log_level, PROJECT_ROOT / cfg.research.runs_dir / "xquant.log.jsonl")
    mem = ResearchMemory(cfg.research.memory_path)
    out = MLStudy(load_spec(args.spec), mem, offline=args.offline).run()
    md, js = write_report(out)
    mem.update_run(out["run_id"], report_path=str(md.relative_to(PROJECT_ROOT)))
    render_dashboard(mem)
    for r in out["results"]:
        print(f"{r['asset']}: {r['status']} | Sharpe {r['primary'].get('sharpe', float('nan')):.2f} CI {r['sharpe_ci']} | {r['checks']}")
    print(f"\n{out['verdict']}\nreport: {md}")
    return 0


def _lab_db(args: argparse.Namespace) -> str:
    return args.memory or str(PROJECT_ROOT / load_config("EURUSD").research.memory_path)


def cmd_queue(args: argparse.Namespace) -> int:
    from xquant.lab.queue import Queue
    q = Queue(_lab_db(args))
    if args.action == "add":
        params: dict[str, Any] = {k: v for k, v in {"asset": args.asset, "spec": args.spec, "mode": args.mode,
                                                    "max_minutes": args.max_minutes, "focus": args.focus}.items() if v}
        if args.online:
            params["offline"] = False
        jid, created = q.add(args.kind, params, priority=args.priority, depends_on=args.depends or [],
                             reason=args.reason or "", force=args.force)
        print(f"{jid} {'queued' if created else 'already exists (duplicate refused; use --force to repeat)'}")
    elif args.action == "list":
        for j in q.jobs(args.status, args.limit):
            print(f"{j['id']} {j['status']:9s} p{j['priority']} {j['department']:16s} {j['kind']:9s} {j['params']} "
                  f"attempts {j['attempts']}/{j['max_attempts']} {(j['error'] or '').splitlines()[-1:] if j['error'] else ''}")
    elif args.action == "cancel":
        print("cancelled" if q.cancel(args.job) else "not cancelled (only QUEUED jobs can be cancelled)")
    q.close()
    return 0


def cmd_worker(args: argparse.Namespace) -> int:
    from xquant.lab.queue import run_worker
    counts = run_worker(_lab_db(args), department=args.department, max_jobs=args.max_jobs, idle_exit_s=args.idle_exit,
                        stale_after_s=args.stale_after)
    print(json.dumps(counts))
    return 0


def cmd_lab(args: argparse.Namespace) -> int:
    from xquant.lab.queue import lab_status
    st = lab_status(_lab_db(args))
    out = PROJECT_ROOT / "research_output" / "lab_status.json"
    out.write_text(json.dumps(st, indent=1, default=str), encoding="utf-8")
    print(json.dumps(st, indent=1, default=str))
    return 0


def cmd_director(args: argparse.Namespace) -> int:
    from xquant.lab.director import enqueue, make_plan
    from xquant.lab.queue import Queue
    from xquant.memory.store import ResearchMemory
    plan = make_plan(ResearchMemory(_lab_db(args)), max_new=args.max_new)
    queued = enqueue(plan, Queue(_lab_db(args))) if args.action == "run" else []
    for d in plan.decisions:
        print(f"PLAN   {d.priority:11s} {d.kind:9s} {d.params} - {d.reason}")
    for jid, created, d in queued:
        print(f"QUEUED {jid} {'new' if created else 'already queued/done'} {d.kind} {d.params}")
    for s in plan.skipped:
        print(f"SKIP   {s}")
    for h in plan.human_actions:
        print(f"HUMAN  {h}")
    return 0


def cmd_autonomous(args: argparse.Namespace) -> int:
    """Director -> queue -> workers, repeated until nothing is left to research or a budget ends."""
    import time as _t

    from xquant.lab.director import enqueue, make_plan
    from xquant.lab.queue import Queue, lab_status, run_worker
    from xquant.memory.store import ResearchMemory
    db, t0 = _lab_db(args), _t.time()
    for cycle in range(1, args.cycles + 1):
        plan = make_plan(ResearchMemory(db), max_new=args.max_new)
        q = Queue(db)
        new = [jid for jid, created, _ in enqueue(plan, q) if created]
        pending = len(q.jobs("QUEUED", 1000))
        q.close()
        print(f"cycle {cycle}: director queued {len(new)} new job(s), {pending} pending; human actions: {plan.human_actions}")
        if not pending:
            print("NOTHING LEFT TO RESEARCH with the data on disk - stopping (see SKIP/HUMAN items: data or a human step needed)")
            break
        hours_left = args.max_hours - (_t.time() - t0) / 3600
        if hours_left <= 0:
            print("time budget reached - stopping")
            break
        print(json.dumps(run_worker(db, max_jobs=pending, idle_exit_s=30, poll_s=5)))
    (PROJECT_ROOT / "research_output" / "lab_status.json").write_text(json.dumps(lab_status(db), indent=1, default=str))
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
    dt = sub.add_parser("daytrade", help="run a pre-registered 10-point day-trading strategy study once")
    dt.add_argument("--spec", required=True, help="strategy YAML (configs/strategies/*.yaml)")
    dt.add_argument("--offline", action="store_true", help="use cached data only")
    dt.add_argument("--memory", help="research memory path")
    dt.set_defaults(fn=cmd_daytrade)
    ml = sub.add_parser("ml", help="run the pre-registered walk-forward ML study once")
    ml.add_argument("--spec", required=True)
    ml.add_argument("--offline", action="store_true")
    ml.add_argument("--memory")
    ml.set_defaults(fn=cmd_ml)
    qu = sub.add_parser("queue", help="research queue: add / list / cancel jobs")
    qu.add_argument("action", choices=["add", "list", "cancel"])
    qu.add_argument("kind", nargs="?", help="add: research|confirm|allocate|daytrade|ml|data|compact")
    qu.add_argument("--asset")
    qu.add_argument("--spec")
    qu.add_argument("--mode", choices=["quick", "standard", "deep"])
    qu.add_argument("--max-minutes", type=float)
    qu.add_argument("--focus", nargs="+")
    qu.add_argument("--online", action="store_true", help="allow downloads (default: cached data only)")
    qu.add_argument("--priority", default="NORMAL", choices=["URGENT", "HIGH_VALUE", "NORMAL", "EXPLORATORY", "LOW"])
    qu.add_argument("--depends", nargs="+", help="job ids that must be DONE first")
    qu.add_argument("--reason", help="why this experiment (kept in the job record)")
    qu.add_argument("--force", action="store_true", help="queue even if an identical job exists")
    qu.add_argument("--job", help="cancel: job id")
    qu.add_argument("--status", help="list: filter by status")
    qu.add_argument("--limit", type=int, default=50)
    qu.add_argument("--memory")
    qu.set_defaults(fn=cmd_queue)
    wk = sub.add_parser("worker", help="run a worker (agent) that executes queued jobs")
    wk.add_argument("--department", help="only take jobs of this department")
    wk.add_argument("--max-jobs", type=int)
    wk.add_argument("--idle-exit", type=float, default=0.0, help="exit after this many idle seconds (0 = never)")
    wk.add_argument("--stale-after", type=int, default=300, help="seconds without heartbeat before a job is recovered")
    wk.add_argument("--memory")
    wk.set_defaults(fn=cmd_worker)
    lb = sub.add_parser("lab", help="real lab status (agents, jobs, research counts) -> research_output/lab_status.json")
    lb.add_argument("action", choices=["status"])
    lb.add_argument("--memory")
    lb.set_defaults(fn=cmd_lab)
    di = sub.add_parser("director", help="research director: plan (dry run) or run (queue the plan)")
    di.add_argument("action", choices=["plan", "run"])
    di.add_argument("--max-new", type=int, default=5)
    di.add_argument("--memory")
    di.set_defaults(fn=cmd_director)
    au = sub.add_parser("autonomous", help="autonomous research mode: director -> queue -> workers, repeated")
    au.add_argument("--cycles", type=int, default=3)
    au.add_argument("--max-hours", type=float, default=6.0)
    au.add_argument("--max-new", type=int, default=3)
    au.add_argument("--memory")
    au.set_defaults(fn=cmd_autonomous)
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
