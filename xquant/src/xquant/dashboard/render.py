"""USER DASHBOARD: a self-contained HTML page rendered from the research memory (and the latest report JSON).

``render_dashboard`` writes a static file; ``serve`` re-renders on every request (auto-refresh) so a
long autonomous run can be watched live. No external assets: charts are inline SVG drawn by a small
vanilla-JS renderer with hover tooltips; all labels are inserted with textContent.
"""

from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from xquant.config import PROJECT_ROOT
from xquant.memory.store import ResearchMemory, unpack

CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--border:rgba(11,11,11,.10);--s1:#2a78d6;--good:#0ca30c;--warn:#fab219;
--serious:#ec835a;--crit:#d03b3b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;
--ink:#fff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1200px;margin:0 auto;padding:20px 16px 48px}body{overflow-x:hidden}h1{font-size:20px;margin:0 0 4px}h2{font-size:15px;margin:0 0 10px}
.sub{color:var(--ink2);margin:0 0 18px}.grid{display:grid;gap:12px}.tiles{grid-template-columns:repeat(auto-fill,minmax(min(140px,45%),1fr))}
.two{grid-template-columns:repeat(auto-fit,minmax(min(340px,100%),1fr))}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;min-width:0}
.tile .k{color:var(--ink2);font-size:12px}.tile .v{font-size:22px;font-weight:600;margin-top:2px;overflow-wrap:anywhere}.tile .v.small{font-size:15px}
.verdict{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-weight:600;font-size:16px}
.badge{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:2px 10px;border:1px solid var(--border);font-size:12px;font-weight:600;white-space:nowrap}
.dot{width:8px;height:8px;border-radius:50%}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--ink2);font-weight:600}td.num{font-variant-numeric:tabular-nums;text-align:right}
.scroll{overflow-x:auto}.log{font:12px/1.5 ui-monospace,Menlo,monospace;max-height:340px;overflow:auto;white-space:pre-wrap;color:var(--ink2)}
.muted{color:var(--muted)}.chart{width:100%;height:220px;position:relative}.chart svg{width:100%;height:100%;display:block}
.tip{position:absolute;pointer-events:none;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:4px 8px;font-size:12px;display:none;white-space:nowrap}
.tip b{font-variant-numeric:tabular-nums}section{margin-top:18px}
"""

JS = r"""
function el(t,a){const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e}
function lineChart(id,xs,ys,fmt,label){
 const box=document.getElementById(id);if(!box||!ys.length)return;const W=box.clientWidth||600,H=box.clientHeight||220,P={l:52,r:12,t:10,b:24};
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':label});box.appendChild(svg);
 let lo=Math.min(...ys),hi=Math.max(...ys);if(lo===hi){lo-=1;hi+=1}const pad=(hi-lo)*.06;lo-=pad;hi+=pad;
 const X=i=>P.l+(W-P.l-P.r)*i/Math.max(1,ys.length-1),Y=v=>P.t+(H-P.t-P.b)*(1-(v-lo)/(hi-lo));
 for(let k=0;k<=4;k++){const v=lo+(hi-lo)*k/4,y=Y(v);svg.appendChild(el('line',{x1:P.l,x2:W-P.r,y1:y,y2:y,stroke:'var(--grid)','stroke-width':1}));
  const t=el('text',{x:P.l-6,y:y+4,'text-anchor':'end','font-size':11,fill:'var(--muted)'});t.textContent=fmt(v);svg.appendChild(t)}
 if(lo<0&&hi>0)svg.appendChild(el('line',{x1:P.l,x2:W-P.r,y1:Y(0),y2:Y(0),stroke:'var(--axis)','stroke-width':1}));
 [0,Math.floor(ys.length/2),ys.length-1].forEach(i=>{const t=el('text',{x:X(i),y:H-6,'text-anchor':i===0?'start':i===ys.length-1?'end':'middle','font-size':11,fill:'var(--muted)'});t.textContent=xs[i];svg.appendChild(t)});
 svg.appendChild(el('path',{d:ys.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(''),fill:'none',stroke:'var(--s1)','stroke-width':2,'stroke-linejoin':'round'}));
 const hair=el('line',{y1:P.t,y2:H-P.b,stroke:'var(--axis)','stroke-width':1,visibility:'hidden'}),dot=el('circle',{r:4,fill:'var(--s1)',stroke:'var(--surface)','stroke-width':2,visibility:'hidden'});
 svg.appendChild(hair);svg.appendChild(dot);const tip=document.createElement('div');tip.className='tip';box.appendChild(tip);
 svg.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect(),x=(e.clientX-r.left)*W/r.width;const i=Math.max(0,Math.min(ys.length-1,Math.round((x-P.l)/(W-P.l-P.r)*(ys.length-1))));
  hair.setAttribute('x1',X(i));hair.setAttribute('x2',X(i));hair.setAttribute('visibility','visible');dot.setAttribute('cx',X(i));dot.setAttribute('cy',Y(ys[i]));dot.setAttribute('visibility','visible');
  tip.textContent='';const b=document.createElement('b');b.textContent=fmt(ys[i]);tip.appendChild(b);tip.appendChild(document.createTextNode('  '+xs[i]));tip.style.display='block';
  tip.style.left=Math.min(X(i)*r.width/W+8,r.width-tip.offsetWidth-4)+'px';tip.style.top='4px'});
 svg.addEventListener('pointerleave',()=>{hair.setAttribute('visibility','hidden');dot.setAttribute('visibility','hidden');tip.style.display='none'});
}
function barChart(id,labels,vals){
 const box=document.getElementById(id);if(!box||!vals.length)return;const W=box.clientWidth||600,rowH=26,P={l:200,r:40},H=vals.length*rowH+8;box.style.height=H+'px';
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'attacks that eliminated candidates'});box.appendChild(svg);const mx=Math.max(...vals);
 const tip=document.createElement('div');tip.className='tip';box.appendChild(tip);
 vals.forEach((v,i)=>{const y=4+i*rowH,w=(W-P.l-P.r)*v/mx;const t=el('text',{x:P.l-8,y:y+15,'text-anchor':'end','font-size':12,fill:'var(--ink2)'});t.textContent=labels[i];svg.appendChild(t);
  const r=el('rect',{x:P.l,y:y+3,width:Math.max(w,2),height:rowH-8,rx:4,fill:'var(--s1)'});svg.appendChild(r);
  const n=el('text',{x:P.l+w+6,y:y+15,'font-size':12,fill:'var(--ink)'});n.textContent=v;svg.appendChild(n);
  const hit=el('rect',{x:0,y:y,width:W,height:rowH,fill:'transparent'});hit.addEventListener('pointerenter',()=>{r.setAttribute('opacity',.8);tip.textContent=labels[i]+': '+v+' candidates';tip.style.display='block';tip.style.left=P.l+'px';tip.style.top=(y-22)+'px'});
  hit.addEventListener('pointerleave',()=>{r.setAttribute('opacity',1);tip.style.display='none'});svg.appendChild(hit)});
}
const D=JSON.parse(document.getElementById('data').textContent);
if(D.equity){lineChart('eq',D.equity.dates,D.equity.values.map(v=>Math.expm1(v)*100),v=>v.toFixed(1)+'%','equity curve');
 let pk=-1e9;const dd=D.equity.values.map(v=>{pk=Math.max(pk,v);return -(1-Math.exp(v-pk))*100});lineChart('dd',D.equity.dates,dd,v=>v.toFixed(1)+'%','drawdown')}
if(D.fails)barChart('fails',D.fails.labels,D.fails.values);
"""

STATUS_COLOR = {"ROBUST": "good", "PASSED_SELECTION": "good", "EDGE FOUND (provisional)": "good", "UNVALIDATED": "warn",
                "OVERFIT": "serious", "REJECTED": "crit", "NO EDGE FOUND": "crit", "INSUFFICIENT DATA": "warn",
                "RUNNING": "warn", "FINISHED": "good"}
ICON = {"good": "&#10003;", "warn": "!", "serious": "&#9888;", "crit": "&#10007;"}


def _badge(status: str) -> str:
    c = STATUS_COLOR.get(status, "warn")
    return (f'<span class="badge"><span class="dot" style="background:var(--{c})"></span>'
            f'{ICON[c]} {html.escape(status)}</span>')


def _e(x: Any) -> str:
    return html.escape(str(x))


def _num(x: Any, pct: bool = False, nd: int = 2) -> str:
    if x is None:
        return "n/a"
    try:
        return f"{float(x):.{nd}%}" if pct else f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return _e(x)


def _latest_report(run_id: str | None) -> dict[str, Any]:
    if not run_id:
        return {}
    for p in sorted((PROJECT_ROOT / "research_output" / "reports").glob(f"{run_id}_*.json")):
        try:
            return dict(json.loads(p.read_text()))
        except Exception:
            return {}
    return {}


def build_html(mem: ResearchMemory, refresh: int | None = None) -> str:
    runs = mem.query("SELECT * FROM research_runs ORDER BY started_at DESC LIMIT 10")
    run = runs[0] if runs else None
    rid = run["id"] if run else None
    counts = mem.counts()
    rep = _latest_report(rid)
    ds = rep.get("dataset", {})
    progress = json.loads(run["progress"] or "{}") if run else {}
    strategies = mem.query("SELECT id, description, status, score, dossier FROM strategies ORDER BY "
                           "CASE status WHEN 'ROBUST' THEN 0 WHEN 'UNVALIDATED' THEN 1 WHEN 'PASSED_SELECTION' THEN 2 ELSE 3 END,"
                           " score DESC LIMIT 12")
    lines = mem.query("SELECT * FROM research_lines WHERE run_id = ?", (rid,)) if rid else []
    logs = mem.query("SELECT at, level, message FROM log ORDER BY id DESC LIMIT 60")
    exps = mem.query("SELECT id, kind, line, status, conclusion, created_at FROM experiments ORDER BY id DESC LIMIT 15")
    data: dict[str, Any] = {}
    best = unpack(strategies[0]["dossier"], {}) if strategies else None
    if best and best.get("equity", {}).get("combined"):
        data["equity"] = {"dates": best["equity"]["dates"], "values": best["equity"]["combined"]}
    fails = rep.get("failure_summary", {})
    if fails:
        data["fails"] = {"labels": list(fails)[:12], "values": list(fails.values())[:12]}
    P: list[str] = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
                    '<meta name="viewport" content="width=device-width,initial-scale=1">',
                    f'<meta http-equiv="refresh" content="{refresh}">' if refresh else "",
                    "<title>X-QUANT Research Dashboard</title><style>", CSS, "</style></head><body><main>",
                    "<h1>X-QUANT Research Dashboard</h1>",
                    '<p class="sub">Research / backtest only - no live trading. Statistical evidence, not investment advice.</p>']
    P += _control_center(mem)
    verdict = (run or {}).get("verdict") or ((run or {}).get("status") or "NO RUNS YET")
    P.append(f'<div class="card verdict">{_badge(verdict)}<span>{_e(rid or "")} {_e((run or {}).get("asset", ""))}</span>'
             f'<span class="muted" style="font-weight:400">{_e(json.loads((run or {}).get("summary") or "{}").get("detail", ""))}</span></div>')
    tiles = [("Dataset", ds.get("symbol", (run or {}).get("asset", "n/a"))), ("Period", f"{ds.get('start', '')[:7]} to {ds.get('end', '')[:7]}"),
             ("Experiments", counts["experiments"]), ("Hypotheses", counts["hypotheses"]),
             ("Hyp. validated", counts["hypotheses_validation"]), ("Strategies", counts["strategies"]),
             ("Rejected", counts["strategies_rejected"]), ("Overfit", counts["strategies_overfit"]),
             ("Passed selection", counts["strategies_passed_selection"]), ("Robust", counts["strategies_robust"])]
    P.append('<section><h2>Research status</h2><div class="grid tiles">' + "".join(
        f'<div class="card tile"><div class="k">{_e(k)}</div><div class="v{" small" if len(str(v)) > 10 else ""}">{_e(v)}</div></div>'
        for k, v in tiles) + "</div></section>")
    P.append('<section class="grid two"><div class="card"><h2>Current research</h2><table>'
             + "".join(f"<tr><th>{_e(k)}</th><td>{_e(v)}</td></tr>" for k, v in
                       [("Run", rid), ("Status", (run or {}).get("status")), ("Mode", (run or {}).get("mode")),
                        ("Phase", progress.get("phase")), ("Active line", progress.get("line", "-")),
                        ("Line run", progress.get("line_run", "-")), ("Experiments (run)", progress.get("experiments")),
                        ("Strategies examined", progress.get("examined")), ("Elapsed (min)", progress.get("elapsed_min")),
                        ("Dataset version", (run or {}).get("dataset_version")), ("Code version", (run or {}).get("code_version"))])
             + "</table></div>")
    P.append('<div class="card"><h2>Research lines</h2><div class="scroll"><table><tr><th>Line</th><th>Status</th><th>Runs</th><th>Stop reason</th></tr>'
             + "".join(f"<tr><td>{_e(x['name'])}</td><td>{_e(x['status'])}</td><td class='num'>{x['experiments']}</td><td>{_e(x['stop_reason'])}</td></tr>"
                       for x in lines) + "</table></div></div></section>")
    P.append('<section class="grid two"><div class="card"><h2>Top-ranked candidate - equity (train+validation, 1x notional, net of costs)</h2>'
             + (f'<p class="muted">{_e(best["strategy_id"])} {_badge(best["status"])} {_e(best["description"])}</p>' if best else "<p class='muted'>No strategy examined yet.</p>")
             + '<div id="eq" class="chart"></div></div><div class="card"><h2>Drawdown</h2><div id="dd" class="chart"></div></div></section>')
    rows = []
    for s in strategies:
        d = unpack(s["dossier"], {})
        v, t, f = d.get("validation", {}), d.get("test", {}), d.get("final", {})
        rows.append(f"<tr><td>{_e(s['id'])}</td><td>{_badge(s['status'])}</td><td>{_e(s['description'])}</td>"
                    f"<td class='num'>{_num(s['score'])}</td><td class='num'>{_num(v.get('sharpe'))}</td><td class='num'>{_num(v.get('sortino'))}</td>"
                    f"<td class='num'>{_num(v.get('profit_factor'))}</td><td class='num'>{_num(v.get('cagr'), True)}</td>"
                    f"<td class='num'>{_num(v.get('max_drawdown'), True)}</td><td class='num'>{v.get('trades', 'n/a')}</td>"
                    f"<td class='num'>{_num((v.get('expectancy') or 0) * 1e4, nd=1)}</td><td class='num'>{_num(t.get('sharpe')) if t else '-'}</td>"
                    f"<td class='num'>{_num(f.get('sharpe')) if f else '-'}</td></tr>")
    P.append('<section class="card"><h2>Strategies (validation metrics; TEST/FINAL shown only once opened)</h2><div class="scroll"><table>'
             "<tr><th>ID</th><th>Status</th><th>Rules</th><th>Score</th><th>SR</th><th>Sortino</th><th>PF</th><th>CAGR</th><th>Max DD</th>"
             "<th>Trades</th><th>Exp. bps</th><th>TEST SR</th><th>FINAL SR</th></tr>" + "".join(rows) + "</table></div></section>")
    P.append('<section class="card"><h2>Why candidates failed</h2><div id="fails" class="chart"></div>'
             + ("" if fails else "<p class='muted'>No examined candidates yet.</p>") + "</section>")
    sc = rep.get("scenario", {})
    macro_rows = "".join(f"<tr><td>{_e(k)}</td><td class='num'>{_num(v['value'], nd=3)}</td><td>{_e(v['as_of_bar'])}</td></tr>"
                         for k, v in ds.get("exog_latest", {}).items())
    ev_note = ("No economic calendar with consensus is connected: upcoming/recent events, surprises and historical "
               "event impact are INSUFFICIENT DATA. Configure <code>asset.calendar_source</code> (econ_calendar_csv).")
    scen = ""
    if sc.get("status") == "OK":
        scen = (f"<p class='muted'>As of {_e(sc['as_of'])}, next {sc['horizon']} bars - n={sc['sample_size']} ({_e(sc['period'])}); "
                f"vs baseline p={_num(sc['p_value_vs_baseline'], nd=3)} - {'informative' if sc['informative'] else 'NOT informative'}</p>"
                "<div class='scroll'><table><tr><th>Scenario</th><th>Definition</th><th>Prob.</th><th>95% CI</th><th>Baseline</th></tr>"
                + "".join(f"<tr><td>{_e(k)}</td><td>{_e(v['definition'])}</td><td class='num'>{_num(v['probability'], True, 1)}</td>"
                          f"<td class='num'>{_num(v['ci95'][0], True, 0)}-{_num(v['ci95'][1], True, 0)}</td><td class='num'>{_num(sc['baseline'].get(k), True, 1)}</td></tr>"
                          for k, v in sc["scenarios"].items()) + "</table></div>"
                + "".join(f"<p class='muted'>{_e(n)}</p>" for n in sc.get("notes", [])))
    P.append(f'<section class="grid two"><div class="card"><h2>Macro dashboard</h2><p class="muted">{ev_note}</p>'
             f'<div class="scroll"><table><tr><th>Series (point-in-time)</th><th>Latest</th><th>Usable from bar</th></tr>{macro_rows}</table></div></div>'
             f'<div class="card"><h2>Scenario analysis</h2>{scen or "<p class=muted>Not available.</p>"}</div></section>')
    P.append('<section class="grid two"><div class="card"><h2>Research log</h2><div class="log">'
             + "\n".join(f"{_e(r['at'][11:19])} {_e(r['message'])}" for r in logs) + "</div></div>"
             '<div class="card"><h2>Latest experiments</h2><div class="scroll"><table><tr><th>ID</th><th>Kind</th><th>Conclusion</th></tr>'
             + "".join(f"<tr><td>{_e(x['id'])}</td><td>{_e(x['line'])}</td><td>{_e((x['conclusion'] or '')[:140])}</td></tr>" for x in exps)
             + "</table></div></div></section>")
    payload = json.dumps(data).replace("</", "<\\/")
    P.append(f'<script type="application/json" id="data">{payload}</script><script>{JS}</script></main></body></html>')
    return "".join(P)


def _control_center(mem: ResearchMemory) -> list[str]:
    """CONTROL CENTER: every figure comes from the database (agents = live workers, jobs = queue rows). No activity is
    shown when nothing runs."""
    from xquant.lab.queue import lab_status
    try:
        st = lab_status(mem.path)
    except Exception as exc:  # the research view must still render
        return [f'<section class="card"><h2>Control center</h2><p class="muted">unavailable: {_e(exc)}</p></section>']
    raw_tiers = st.get("strategy_tiers")
    tiers: dict[str, int] = raw_tiers if isinstance(raw_tiers, dict) else {}
    jobs = st["jobs"]
    hyp = st["hypotheses"]
    tiles = [("Lab status", st["lab"].split(" ")[0]), ("Active agents", st["active_agents"]),
             ("Running jobs", jobs.get("RUNNING", 0)), ("Queued", jobs.get("QUEUED", 0)),
             ("Jobs done / failed", f"{jobs.get('DONE', 0)} / {jobs.get('FAILED', 0)}"),
             ("Hypotheses", sum(hyp.values())), ("Strategies examined", sum(st["strategies"].values())),
             ("Validated", tiers.get("VALIDATED", 0)), ("Elite", tiers.get("ELITE", 0)), ("Destroyed", tiers.get("DESTROYED", 0)),
             ("Experiments", st["experiments"]), ("Research hours (queue)", st["research_hours_queue"]),
             ("Open alerts", len(st["open_alerts"]))]
    P = ['<section><h2>Control center</h2><div class="grid tiles">' + "".join(
        f'<div class="card tile"><div class="k">{_e(k)}</div><div class="v{" small" if len(str(v)) > 10 else ""}">{_e(v)}</div></div>'
        for k, v in tiles) + "</div></section>"]
    agents = "".join(f"<tr><td>{_e(a['id'])}</td><td>{_e(a['department'])}</td><td>{_e(a['status'])}</td>"
                     f"<td>{_e(a['current_job'] or '')}</td><td>{_e(a['heartbeat_at'])}</td></tr>" for a in st["agents"])
    running = "".join(f"<tr><td>{_e(j['id'])}</td><td>{_e(j['department'])}</td><td>{_e(j['kind'])}</td><td>{_e(j['params'])}</td>"
                      f"<td>{_e(j['started_at'])}</td></tr>" for j in st["running_jobs"])
    alerts = "".join(f"<tr><td>{_e(a['level'])}</td><td>{_e(a['at'])}</td><td>{_e(a['message'])}</td></tr>" for a in st["open_alerts"])
    P.append('<section class="grid two"><div class="card"><h2>Agents (live workers)</h2><div class="scroll"><table>'
             "<tr><th>Agent</th><th>Department</th><th>State</th><th>Job</th><th>Heartbeat</th></tr>"
             + (agents or '<tr><td colspan="5" class="muted">IDLE - no worker running</td></tr>') + "</table></div></div>"
             '<div class="card"><h2>Live experiments</h2><div class="scroll"><table>'
             "<tr><th>Job</th><th>Department</th><th>Kind</th><th>Parameters</th><th>Started</th></tr>"
             + (running or '<tr><td colspan="5" class="muted">none running</td></tr>') + "</table></div></div></section>")
    P.append('<section class="card"><h2>Alerts</h2><div class="scroll"><table><tr><th>Level</th><th>When</th><th>Message</th></tr>'
             + (alerts or '<tr><td colspan="3" class="muted">no open alerts</td></tr>') + "</table></div></section>")
    return P


def render_dashboard(mem: ResearchMemory, out: Path | None = None) -> Path:
    out = out or PROJECT_ROOT / "research_output" / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(mem), encoding="utf-8")
    return out


def serve(memory_path: str, port: int = 8765, refresh: int = 15) -> None:
    class H(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            mem = ResearchMemory(memory_path)
            try:
                body = build_html(mem, refresh).encode()
            finally:
                mem.close()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: Any) -> None:
            pass

    print(f"X-QUANT dashboard on http://127.0.0.1:{port} (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
