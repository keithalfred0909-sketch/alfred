"""X-QUANT RESEARCH REPORT (Markdown + JSON). Every number comes from the research outcome; nothing is
filled in by hand. Sections without evidence say so explicitly."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from xquant.config import PROJECT_ROOT
from xquant.research.orchestrator import ResearchOutcome


def _f(x: Any, pct: bool = False, nd: int = 2) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    if isinstance(x, int | float):
        return f"{x:.{nd}%}" if pct else f"{x:.{nd}f}"
    return str(x)


def _metrics_row(name: str, m: dict[str, Any]) -> str:
    if not m:
        return f"| {name} | not evaluated | | | | | | | | |"
    return (f"| {name} | {_f(m.get('total_return'), True)} | {_f(m.get('cagr'), True)} | {_f(m.get('profit_factor'))} | "
            f"{_f(m.get('sharpe'))} | {_f(m.get('sortino'))} | {_f(m.get('max_drawdown'), True)} | {m.get('trades', 'n/a')} | "
            f"{_f((m.get('expectancy') or 0) * 1e4, nd=1)} bps | {_f(m.get('win_rate'), True)} |")


def _strategy_section(rank: int, d: dict[str, Any]) -> list[str]:
    g = d["genome"]
    L = [f"### Strategy #{rank} - {d['strategy_id']} - **{d['status']}**", "",
         f"**Rules:** {d['description']}", "",
         f"- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); "
         f"fill at the next available price + costs; direction {'LONG' if g['direction'] > 0 else 'SHORT'}",
         f"- Exit: after {g['hold']} bars" + (f", or stop at {g['stop']} x vol x sqrt(hold)" if g.get('stop') else "")
         + (f", or take-profit at {g['take']} x vol x sqrt(hold)" if g.get('take') else ""),
         "- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill",
         f"- Complexity: {d['complexity']}  |  Composite score: {_f(d.get('score'))}", "",
         "**Performance**", "",
         "| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |",
         "|---|---|---|---|---|---|---|---|---|---|",
         _metrics_row("TRAIN (in-sample)", d.get("train", {})),
         _metrics_row("VALIDATION", d.get("validation", {})),
         _metrics_row("TEST", d.get("test", {})),
         _metrics_row("FINAL out-of-sample", d.get("final", {})), ""]
    wf = d.get("walk_forward", {}).get("rolling", {})
    wfe = d.get("walk_forward", {}).get("expanding", {})
    L += [f"**Walk-forward:** rolling OOS Sharpe {_f(wf.get('oos_sharpe'))}, positive windows {_f(wf.get('positive_windows'), True)}, "
          f"efficiency {_f(wf.get('efficiency'))}; expanding OOS Sharpe {_f(wfe.get('oos_sharpe'))}", ""]
    mc = d.get("monte_carlo", {})
    tb, re = mc.get("trade_bootstrap", {}), mc.get("random_entry", {})
    L += [f"**Monte Carlo:** P(loss) under trade bootstrap {_f(tb.get('p_loss'), True)}, 95th pct max DD {_f(tb.get('max_dd_p95'), True)}; "
          f"random-entry test p = {_f(re.get('p_value'), nd=3)}", ""]
    rb = d.get("robustness", {})
    costs = rb.get("costs", {})
    L += ["**Stress tests:** " + ", ".join(f"{k}: SR {_f(v.get('sharpe'))}" for k, v in costs.items()), ""]
    pp = rb.get("parameters", {})
    L += [f"**Robustness:** parameter neighbours profitable {_f(pp.get('profitable_share'), True)}; "
          f"noise-perturbed runs SR>0 {_f(rb.get('data_noise', {}).get('positive_share'), True)}; "
          f"profitable years {_f(rb.get('breakdowns', {}).get('profitable_year_share'), True)}", ""]
    ov = d.get("overfit", {})
    L += [f"**Overfitting risk:** deflated Sharpe probability {_f(ov.get('deflated_sharpe', {}).get('dsr'), nd=3)} "
          f"(after {ov.get('deflated_sharpe', {}).get('n_trials', 'n/a')} trials); PBO {_f(ov.get('pbo', {}).get('pbo'), nd=2)}; "
          f"IS->OOS Sharpe ratio {_f(ov.get('is_oos_degradation'))}", ""]
    passed = [a for a in d["attacks"] if a["passed"] is True]
    failed = [a for a in d["attacks"] if a["passed"] is False]
    L += ["**Adversarial attacks**", "", "| Attack | Kind | Result | Value | Threshold |", "|---|---|---|---|---|"]
    for a in d["attacks"]:
        res = "PASS" if a["passed"] is True else "FAIL" if a["passed"] is False else "n/a"
        val = json.dumps(a["value"], default=str) if not isinstance(a["value"], float) else _f(a["value"], nd=3)
        L.append(f"| {a['name']} | {a['kind']} | {res} | {val[:60]} | {a['threshold']} |")
    L += ["", f"**Why it {'survived' if d['status'] == 'ROBUST' else 'is ranked here'}:** "
          f"passed {len(passed)} of {len(passed) + len(failed)} decisive/informative attacks.", ""]
    L += ["**Why it might fail:** " + ("; ".join(d["reasons"]) if d["reasons"] else
                                       "regime change, structural break in the asset, cost increases, crowding; "
                                       "historical robustness is not a guarantee."), ""]
    return L


def build_markdown(o: ResearchOutcome) -> str:
    ds = o.dataset
    L = ["# X-QUANT RESEARCH REPORT", "",
         f"> **VERDICT: {o.verdict}** - {o.verdict_detail}", "",
         "Research/backtest output only. Not investment advice. No live trading.", "",
         "| | |", "|---|---|",
         f"| Run | {o.run_id} |", f"| Asset | {o.asset} |",
         f"| Timeframe | {ds.get('timeframe', 'n/a')} |",
         f"| Historical period | {ds.get('start', 'n/a')} to {ds.get('end', 'n/a')} ({ds.get('rows', 'n/a')} bars) |",
         f"| Data capabilities | {ds.get('capabilities', 'n/a')} |",
         f"| Dataset version | {ds.get('version', 'n/a')} |",
         f"| Mode / budget used | {o.budget.get('mode')} - {o.budget.get('experiments_used')} experiments, "
         f"{o.budget.get('strategies_examined')} strategies examined, {o.budget.get('minutes_used')} min |",
         f"| Backtests counted as trials (all runs on this dataset) | {o.trials.get('n_trials', 'n/a')} |", ""]
    if o.splits:
        L += ["**Splits** (chronological, embargoed): " + "; ".join(
            f"{k.upper()} {v['span'][0]} to {v['span'][1]} ({v['bars']} bars)" for k, v in o.splits.items()), ""]
    L += ["## Data", ""] + [f"- {n}" for n in ds.get("notes", [])]
    q = ds.get("quality_report", {})
    if q:
        L.append(f"- Quality {q.get('verdict')}: {q.get('rows_in')} raw rows -> {q.get('rows_out')} bars; "
                 f"{q.get('missing_close')} missing (holidays/no fix), {q.get('exact_duplicates')} duplicates, "
                 f"{q.get('non_positive')} corrupt, {q.get('spikes_removed')} bad prints removed, gaps {q.get('gaps')}")
    for k, m in ds.get("exogenous_meta", {}).items():
        L.append(f"- Exogenous `{k}`: {m.get('status')} - {m.get('description', '')} (lag {m.get('lag_days')} days)")
    L += [""]

    def sect(title: str, engine: str) -> None:
        fs = [f for f in o.findings if f["engine"] == engine]
        disc = [f for f in fs if f["status"] == "DISCOVERY"]
        insuf = [f for f in fs if f["status"] == "INSUFFICIENT DATA"]
        tested = [f for f in fs if f["status"] not in ("DESCRIPTIVE", "INSUFFICIENT DATA")]
        L.extend([f"## {title}", "",
                  f"{len(tested)} statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. "
                  f"**Replicated discoveries: {len(disc)}.**", ""])
        for f in disc:
            L.append(f"- **{f['name']}** - {f['description']}: effect {_f(f['effect'], nd=5)}, p={_f(f['p_value'], nd=5)}, "
                     f"q={_f(f['q_value'], nd=4)}, replication p={_f(f['replication_p'], nd=5)} (n={f['n']})")
        nrep = [f for f in fs if f["status"] == "NOT_REPLICATED"]
        for f in nrep:
            L.append(f"- Not replicated: {f['name']} (train p={_f(f['p_value'], nd=5)}, validation p={_f(f['replication_p'], nd=4)})")
        for f in [f for f in fs if f["status"] == "DESCRIPTIVE"]:
            det = {k: v for k, v in f["details"].items() if k not in ("centroids", "bic", "series")}
            L.append(f"- Descriptive - {f['name']}: {f['description']} {json.dumps(det, default=str)[:400]}")
        if insuf:
            L.append(f"- INSUFFICIENT DATA for: {', '.join(f['name'] for f in insuf)}")
        L.append("")

    sect("Market discoveries", "market")
    sect("Macro discoveries", "macro")
    sect("News discoveries", "news")
    fe = o.features
    L += ["## Feature discovery", "",
          f"{fe.get('candidates', 0)} candidate features, {fe.get('tests', 0)} (feature, horizon) IC tests on the discovery "
          f"part of TRAIN; confirmed on the inner holdout: **{len(fe.get('confirmed', []))}** {fe.get('confirmed', [])[:10]}",
          f"Status counts: {fe.get('status_counts', {})}", ""]
    hy = o.hypotheses
    L += ["## Top hypotheses", "",
          f"{hy.get('generated', 0)} hypotheses ({hy.get('new', 0)} new, {hy.get('reused', 0)} reused from memory). "
          f"Status counts: {hy.get('status_counts', {})}", ""]
    if hy.get("validated"):
        L += ["| ID | Hypothesis | n | effect size | p | q | confirm p | status |", "|---|---|---|---|---|---|---|---|"]
        for h in hy["validated"][:10]:
            L.append(f"| {h['id']} | {h['description']} | {h['sample']} | {_f(h['effect_size'], nd=3)} | {_f(h['p_value'], nd=5)} | "
                     f"{_f(h['q_value'], nd=4)} | {_f(h['confirm_p'], nd=4)} | {h['status']} |")
    else:
        L.append("No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.")
    if hy.get("top_rejected_or_overfit"):
        L += ["", "Strongest hypotheses that failed confirmation (OVERFIT):", ""]
        for h in hy["top_rejected_or_overfit"][:5]:
            L.append(f"- {h['id']}: {h['description']} - discovery p={_f(h['p_value'], nd=5)}, confirmation p={_f(h['confirm_p'], nd=3)}, "
                     f"confirmation effect {_f(h['confirm_effect'], nd=5)} vs {_f(h['effect'], nd=5)}")
    L += ["", "## Research lines", "", "| Line | Status | Runs | Examined | Stop reason |", "|---|---|---|---|---|"]
    for ln in o.lines:
        L.append(f"| {ln['name']} | {ln['status']} | {ln['experiments']} | {ln['examined']} | {ln['stop_reason']} |")
    L += ["", "## Top strategies", ""]
    if not o.ranking:
        L += ["No strategy reached examination.", ""]
    for i, d in enumerate(o.ranking, 1):
        L += _strategy_section(i, d)
    L += ["## Why the others failed", ""]
    if o.failure_summary:
        L += ["Attacks that eliminated candidates (count of candidates failing each):", ""]
        L += [f"- {k}: {v}" for k, v in o.failure_summary.items()]
    statuses: dict[str, int] = {}
    for d in o.dossiers:
        statuses[d["status"]] = statuses.get(d["status"], 0) + 1
    L += ["", f"Final status of all {len(o.dossiers)} examined strategies: {statuses}", ""]
    sc = o.scenario
    L += ["## Scenario analysis (historical frequencies, not forecasts)", ""]
    if sc and sc.get("status") == "OK":
        L += [f"As of {sc['as_of']}, horizon {sc['horizon']} bars. Conditions: {'; '.join(sc['conditions']) or 'none'}",
              f"Sample size {sc['sample_size']} ({sc['period']}).", "",
              "| Scenario | Definition | Probability | 95% CI | Baseline |", "|---|---|---|---|---|"]
        for k, v in sc["scenarios"].items():
            L.append(f"| {k} | {v['definition']} | {_f(v['probability'], True, 1)} | {_f(v['ci95'][0], True, 1)}-{_f(v['ci95'][1], True, 1)} | "
                     f"{_f(sc['baseline'].get(k), True, 1)} |")
        L += ["", f"Test vs baseline: p = {_f(sc['p_value_vs_baseline'], nd=3)} -> "
              f"{'conditions are informative' if sc['informative'] else 'NOT informative'}.",
              f"Invalidated if: {'; '.join(sc['invalidation']) or 'n/a'}", ""] + [f"- {n}" for n in sc.get("notes", [])]
    else:
        L.append(f"Scenario analysis: {sc.get('status', 'not run') if sc else 'not run'}")
    L += ["", "## Protected split access log", ""]
    agg: dict[str, int] = {}
    for e in o.split_access:
        agg[f"{e['split']}/{e['purpose']}"] = agg.get(f"{e['split']}/{e['purpose']}", 0) + 1
    L += [f"- {k}: {v}" for k, v in agg.items()] or ["- none"]
    L += ["", "## Limitations", ""] + [f"- {x}" for x in o.limitations]
    L += ["", "## Confidence", "",
          {"NO EDGE FOUND": "The conclusion 'no robust edge' is conditional on the data available (see limitations), the search "
                            "space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.",
           "INSUFFICIENT DATA": "No conclusion about edges can be drawn."}.get(
              o.verdict, "Provisional: survives every test run here; needs independent validation and paper trading."), ""]
    return "\n".join(L)


def write_report(o: ResearchOutcome, out_dir: Path | None = None) -> tuple[Path, Path]:
    out_dir = out_dir or PROJECT_ROOT / "research_output" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / f"{o.run_id}_{o.asset}.md"
    js = out_dir / f"{o.run_id}_{o.asset}.json"
    md.write_text(build_markdown(o), encoding="utf-8")
    js.write_text(json.dumps(o.__dict__, default=str, indent=1), encoding="utf-8")
    return md, js
