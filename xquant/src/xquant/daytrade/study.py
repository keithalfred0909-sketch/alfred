"""Pre-registered day-trading strategy study (10-point specification) for nq_orb5_v1-style rules.

Pass rule (from the spec): on TRAIN+VALIDATION - mean net R > 0 with stationary-bootstrap 95% CI lower
bound > 0; deflated Sharpe of daily returns >= 0.95 with N = variants registered for this market; >= 50%
profitable years; beats random direction on the same days with the same stops (p < 0.05); still positive
at 2x costs and with the entry delayed one minute. Then TEST once (mean R > 0) and FINAL once (best).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from xquant.config import PROJECT_ROOT, load_config
from xquant.daytrade.orb import OrbParams, daily_returns, run_orb
from xquant.errors import ConfigError
from xquant.memory.store import ResearchMemory
from xquant.stats import sharpe, stationary_bootstrap_indices
from xquant.validation.overfit import deflated_sharpe_report
from xquant.validation.splits import SplitGuard

FAMILY = "DAYTRADE:NAS100"


def load_spec(path: str | Path) -> dict[str, Any]:
    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for k in ("name", "variants", "9_backtest"):
        if not spec.get(k):
            raise ConfigError(f"strategy spec needs '{k}'")
    return spec


def spec_sha256(spec: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(spec, sort_keys=True, default=str).encode()).hexdigest()


def trade_stats(t: pd.DataFrame, days_: pd.Index, rng: np.random.Generator | None = None,
                reps: int = 0) -> dict[str, Any]:
    if t.empty:
        return {"trades": 0}
    days = pd.DatetimeIndex(days_)
    r = t["r_net"].to_numpy()
    dr = daily_returns(t).reindex(days, fill_value=0.0)
    wins, losses = r[r > 0].sum(), -r[r < 0].sum()
    years = (1 + dr).groupby(pd.DatetimeIndex(dr.index).year).prod() - 1
    top = np.sort(r)[::-1][: max(1, int(math.ceil(len(r) * 0.05)))].sum()
    out: dict[str, Any] = {
        "trades": int(len(r)), "trades_per_year": float(len(r) / max(len(days) / 252, 1e-9)),
        "win_rate": float((r > 0).mean()), "mean_r": float(r.mean()), "median_r": float(np.median(r)),
        "profit_factor": float(wins / losses) if losses > 0 else float("inf"),
        "mean_r_gross": float(t["r_gross"].mean()), "mean_cost_r": float(t["cost_r"].mean()),
        "exits": t["reason"].value_counts().to_dict(), "longs": int((t["side"] > 0).sum()),
        "daily_sharpe": float(sharpe(dr.to_numpy(), 252)), "cagr_at_1pct_risk": float(np.prod(1 + dr.to_numpy()) ** (252 / max(len(dr), 1)) - 1),
        "max_drawdown": float((1 - (1 + dr).cumprod() / (1 + dr).cumprod().cummax()).max()),
        "profitable_years": float((years > 0).mean()), "yearly": {int(y): round(float(v), 4) for y, v in zip(years.index.to_numpy(), years.to_numpy(), strict=True)},
        "top5pct_trade_share": float(top / r.sum()) if r.sum() > 0 else float("inf"),
        "avg_risk_taken": float(t["risk_frac"].mean()), "median_stop_pct": float(t["stop_dist_frac"].median() * 100)}
    if rng is not None and reps:
        means = [r[stationary_bootstrap_indices(len(r), 10.0, rng)].mean() for _ in range(reps)]
        out["mean_r_ci"] = [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]
    return out


class DayTradeStudy:
    def __init__(self, spec: dict[str, Any], memory: ResearchMemory, offline: bool = True, seed: int = 11,
                 reps: int = 2000, random_dir_reps: int = 200, bars: pd.DataFrame | None = None,
                 cost_per_fill_frac: float = 0.435e-4) -> None:
        self.spec, self.memory, self.offline, self.bars = spec, memory, offline, bars
        self.sha = spec_sha256(spec)
        self.rng = np.random.default_rng(seed)
        self.reps, self.rd_reps, self.cost = reps, random_dir_reps, cost_per_fill_frac
        self.guard = SplitGuard()

    def _bars(self) -> pd.DataFrame:
        if self.bars is not None:
            return self.bars
        from xquant.data.engine import DataEngine
        bars, _, rep = DataEngine(load_config("NAS100_M1").asset, offline=self.offline).load_bars()
        return bars

    def run(self) -> dict[str, Any]:
        spec = self.spec
        prior = self.memory.registration(spec["name"], FAMILY)
        if prior and prior["sha256"] != self.sha:
            raise ConfigError(f"strategy '{spec['name']}' was registered with different content; register a new version")
        if prior and prior.get("run_id"):
            raise ConfigError(f"strategy '{spec['name']}' already evaluated in {prior['run_id']} ({prior['verdict']})")
        bars = self._bars()
        dv = hashlib.sha256(pd.util.hash_pandas_object(bars[["close"]]).to_numpy().tobytes()).hexdigest()[:16]
        if not prior:
            self.memory.register(spec["name"], FAMILY, dv, self.sha, spec, len(spec["variants"]), [])
        run_id = self.memory.start_run(FAMILY, "daytrade", dv, self.sha[:16], 0)
        n_family = self.memory.registered_variants(FAMILY)
        sp = spec["9_backtest"]["splits"]
        cut = {k: pd.Timestamp(sp[k]) for k in ("train_end", "validation_end", "test_end")}

        def split_of(d: pd.Timestamp) -> str:
            return ("train" if d <= cut["train_end"] else "validation" if d <= cut["validation_end"]
                    else "test" if d <= cut["test_end"] else "final")
        local = pd.DatetimeIndex(bars.index).tz_convert("America/New_York").tz_localize(None)
        all_days = pd.DatetimeIndex(np.unique(local.normalize()))
        hm = np.asarray(local.hour * 60 + local.minute)
        sess_days = pd.DatetimeIndex(np.unique(local.normalize()[(hm == 960)]))  # days with a 16:00 bar
        sp_days = pd.Series([split_of(d) for d in sess_days], index=sess_days)
        prim_days = sp_days.index[sp_days.isin(["train", "validation"]).to_numpy()]
        prim_bars = bars[local < cut["validation_end"] + pd.Timedelta(days=1)]  # robustness runs never see TEST/FINAL
        results = []
        for v in spec["variants"]:
            p = OrbParams(context="weekly_vwap_side" if v.get("context") == "weekly_vwap_side" else "none",
                          cost_per_fill_frac=self.cost)
            t = run_orb(bars, p)
            t["split"] = [split_of(d) for d in t["date"]]
            prim = t[t["split"].isin(["train", "validation"])]
            res: dict[str, Any] = {"variant": v, "primary": trade_stats(prim, prim_days, self.rng, self.reps),
                                   "train": trade_stats(t[t["split"] == "train"], sp_days.index[(sp_days == "train").to_numpy()]),
                                   "validation": trade_stats(t[t["split"] == "validation"],
                                                             sp_days.index[(sp_days == "validation").to_numpy()])}
            dr = daily_returns(prim).reindex(prim_days, fill_value=0.0).to_numpy()
            res["deflated_sharpe"] = deflated_sharpe_report(dr, n_family, 0.0, 252)
            # robustness (all on the primary sample)
            def prim_mean(pp: OrbParams) -> float:
                tt = run_orb(prim_bars, pp)
                return float(tt["r_net"].mean()) if len(tt) else float("nan")
            res["cost_x2_mean_r"] = prim_mean(replace(p, cost_per_fill_frac=2 * self.cost))
            res["cost_x3_mean_r"] = prim_mean(replace(p, cost_per_fill_frac=3 * self.cost))
            res["delay_1m_mean_r"] = prim_mean(replace(p, entry_delay_min=1))
            res["delay_2m_mean_r"] = prim_mean(replace(p, entry_delay_min=2))
            res["neighbours_mean_r"] = {
                "min_body_frac=0.05": prim_mean(replace(p, min_body_frac=0.05)),
                "min_body_frac=0.2": prim_mean(replace(p, min_body_frac=0.2)),
                "target_r=5": prim_mean(replace(p, target_r=5.0)), "target_r=20": prim_mean(replace(p, target_r=20.0)),
                "range_minutes=4": prim_mean(replace(p, range_minutes=4)),
                "range_minutes=6": prim_mean(replace(p, range_minutes=6))}
            actual = res["primary"].get("mean_r", float("nan"))
            null = []
            for _ in range(self.rd_reps):  # random direction on the same trade days, same stops/targets/costs
                sides = {d: int(self.rng.choice([-1, 1])) for d in prim["date"]}
                tt = run_orb(prim_bars, replace(p, direction_override=sides))
                tt = tt[tt["date"].isin(prim["date"])]
                null.append(float(tt["r_net"].mean()) if len(tt) else 0.0)
            res["random_direction"] = {"p_value": float((1 + np.sum(np.array(null) >= actual)) / (1 + len(null))),
                                       "null_mean": float(np.mean(null)), "null_p95": float(np.quantile(null, 0.95))}
            ci = res["primary"].get("mean_r_ci", [float("nan")] * 2)
            res["checks"] = {"mean_r_ci_above_0": bool(ci[0] > 0),
                             "deflated_sharpe": bool(res["deflated_sharpe"]["dsr"] >= 0.95),
                             "profitable_years": bool(res["primary"].get("profitable_years", 0) >= 0.5),
                             "beats_random_direction": bool(res["random_direction"]["p_value"] < 0.05),
                             "cost_x2_positive": bool(res["cost_x2_mean_r"] > 0),
                             "delay_1m_positive": bool(res["delay_1m_mean_r"] > 0)}
            res["status"] = "PASSED_PRIMARY" if all(res["checks"].values()) else "REJECTED"
            res["_trades"] = t
            results.append(res)
        for res in [r for r in results if r["status"] == "PASSED_PRIMARY"]:
            self.guard.request("test", "evaluate", f"daytrade:{spec['name']}:{res['variant']}")
            tt = res["_trades"][res["_trades"]["split"] == "test"]
            res["test"] = trade_stats(tt, sp_days.index[(sp_days == "test").to_numpy()])
            res["status"] = "ROBUST" if res["test"].get("mean_r", -1) > 0 else "REJECTED"
        robust = sorted([r for r in results if r["status"] == "ROBUST"], key=lambda r: -r["primary"]["mean_r"])
        verdict = "NO EDGE FOUND"
        if robust:
            top = robust[0]
            self.guard.request("final", "evaluate", f"daytrade:{spec['name']}:{top['variant']}")
            tf = top["_trades"][top["_trades"]["split"] == "final"]
            top["final"] = trade_stats(tf, sp_days.index[(sp_days == "final").to_numpy()])
            verdict = "EDGE FOUND (provisional)" if top["final"].get("mean_r", -1) > 0 else "NO EDGE FOUND"
        for res in results:
            res["trades_sample"] = res["_trades"].head(5).astype(str).to_dict("records")
            res.pop("_trades")
        out = {"run_id": run_id, "spec": spec, "sha256": self.sha, "dataset_version": dv, "multiple_testing_n": n_family,
               "data": {"start": str(bars.index[0]), "end": str(bars.index[-1]), "minute_bars": int(len(bars)),
                        "calendar_days": int(len(all_days)), "sessions_with_1600_bar": int(len(sess_days))},
               "results": results, "verdict": verdict, "split_access": list(self.guard.log)}
        self.memory.record_split_access(run_id, self.guard.log)
        self.memory.complete_registration(spec["name"], FAMILY, run_id, verdict)
        self.memory.update_run(run_id, status="FINISHED", verdict=verdict, finished_at=pd.Timestamp.now(tz="UTC").isoformat(),
                               summary={"detail": f"daytrade '{spec['name']}': "
                                                  + ", ".join(f"{r['variant']} -> {r['status']}" for r in results)})
        return out


def write_report(out: dict[str, Any], out_dir: Path | None = None) -> tuple[Path, Path]:
    out_dir = out_dir or PROJECT_ROOT / "research_output" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    s = out["spec"]

    def f(x: Any, pct: bool = False) -> str:
        if x is None or (isinstance(x, float) and not math.isfinite(x)):
            return "n/a"
        return f"{x:.2%}" if pct else f"{x:.3f}"
    L = ["# X-QUANT DAY-TRADING STRATEGY STUDY (pre-registered, 10-point specification)", "",
         f"> **VERDICT: {out['verdict']}**", "", "Research/backtest output only. Not investment advice. No live trading.", "",
         f"**{s['name']}** - run {out['run_id']}, spec sha256 `{out['sha256']}`, multiple-testing N = {out['multiple_testing_n']}",
         f"Data: {out['data']}", ""]
    for k in [k for k in s if k[:1].isdigit()] + ["inspiration"]:
        L.append(f"- **{k}**: {s[k] if not isinstance(s[k], dict) else json.dumps(s[k])}")
    L += ["", "| Variant | Status | Trades | Trades/yr | Win rate | Mean R net (95% CI) | gross R | PF | Daily Sharpe | CAGR @1% risk | Max DD | Profitable yrs |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["results"]:
        p = r["primary"]
        ci = p.get("mean_r_ci", [None, None])
        L.append(f"| {r['variant']} | {r['status']} | {p.get('trades')} | {f(p.get('trades_per_year'))} | {f(p.get('win_rate'), True)} | "
                 f"{f(p.get('mean_r'))} ({f(ci[0])}..{f(ci[1])}) | {f(p.get('mean_r_gross'))} | {f(p.get('profit_factor'))} | "
                 f"{f(p.get('daily_sharpe'))} | {f(p.get('cagr_at_1pct_risk'), True)} | {f(p.get('max_drawdown'), True)} | "
                 f"{f(p.get('profitable_years'), True)} |")
    for r in out["results"]:
        L += ["", f"### Variant {r['variant']} - {r['status']}", "", f"- checks: {r['checks']}",
              f"- TRAIN mean R {f(r['train'].get('mean_r'))} ({r['train'].get('trades')} trades); VALIDATION mean R "
              f"{f(r['validation'].get('mean_r'))} ({r['validation'].get('trades')} trades)",
              f"- random direction: p = {f(r['random_direction']['p_value'])}, null mean R {f(r['random_direction']['null_mean'])}",
              f"- costs x2 / x3 mean R: {f(r['cost_x2_mean_r'])} / {f(r['cost_x3_mean_r'])}; entry +1 / +2 min: "
              f"{f(r['delay_1m_mean_r'])} / {f(r['delay_2m_mean_r'])}",
              f"- parameter neighbours (mean R): {{{', '.join(f'{k}: {f(v)}' for k, v in r['neighbours_mean_r'].items())}}}",
              f"- deflated Sharpe {f(r['deflated_sharpe']['dsr'])}; top 5% trades share of profit {f(r['primary'].get('top5pct_trade_share'))}",
              f"- exits {r['primary'].get('exits')}; median stop {f(r['primary'].get('median_stop_pct'))}% of price; "
              f"average risk actually taken {f(r['primary'].get('avg_risk_taken'), True)}",
              f"- yearly returns at 1% risk: {r['primary'].get('yearly')}"]
        for k in ("test", "final"):
            if k in r:
                L.append(f"- {k.upper()}: mean R {f(r[k].get('mean_r'))}, {r[k].get('trades')} trades, CAGR @1% {f(r[k].get('cagr_at_1pct_risk'), True)}")
    L += ["", "## Protected split access", ""] + ([f"- {e['split']}/{e['purpose']}: {e['who']}" for e in out["split_access"]]
                                                  or ["- none (no variant passed the primary sample)"])
    L += ["", "## Limitations", "", "- Dukascopy CFD minute mid prices as a proxy for NQ futures; tick volume (weekly VWAP context) is not CME volume.",
          "- No news calendar filter (not available reliably); costs are fixed per fill (no market-impact model).", ""]
    md = out_dir / f"{out['run_id']}_DAYTRADE_{s['name']}.md"
    js = out_dir / f"{out['run_id']}_DAYTRADE_{s['name']}.json"
    md.write_text("\n".join(L), encoding="utf-8")
    js.write_text(json.dumps(out, default=str, separators=(",", ":")), encoding="utf-8")
    return md, js
