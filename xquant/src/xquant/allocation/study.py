"""ALLOCATION STUDIES: pre-registered portfolio / position-sizing hypotheses (no entry-exit genomes).

Same scientific contract as confirmatory mode: the spec is hashed and runs once; the multiple-testing N is
the number of allocation variants ever registered; the primary sample is TRAIN+VALIDATION (these rules
fit nothing except, for volatility management, an exposure scale on TRAIN); TEST is opened once for
variants that pass, FINAL once for the best of those.

Mechanics: daily sessions closing 17:00 New York built from validated hourly Dukascopy candles. Weights
decided at the close of day t apply to the simple return of day t+1. Costs: |change in weight| times the
per-instrument cost per unit of turnover, charged on day t+1. Weights are held constant between
rebalances (a standard research simplification: real positions drift with prices).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from xquant.allocation import rules
from xquant.config import PROJECT_ROOT
from xquant.data.cleaning import clean_bars
from xquant.data.sources.base import build_source
from xquant.data.sources.resample import aggregate_sessions
from xquant.errors import ConfigError
from xquant.memory.store import ResearchMemory
from xquant.stats import sharpe, stationary_bootstrap_indices
from xquant.validation.overfit import deflated_sharpe_report
from xquant.validation.splits import SplitGuard

INSTRUMENTS: dict[str, dict[str, Any]] = {
    "EURUSD": {"instrument": "EURUSD", "point": 1e-5, "start": "2005-01-01"},
    "GBPUSD": {"instrument": "GBPUSD", "point": 1e-5, "start": "2005-01-01"},
    "USDJPY": {"instrument": "USDJPY", "point": 1e-3, "start": "2005-01-01"},
    "USDCAD": {"instrument": "USDCAD", "point": 1e-5, "start": "2005-01-01"},
    "USDCHF": {"instrument": "USDCHF", "point": 1e-5, "start": "2005-01-01"},
    "USDSEK": {"instrument": "USDSEK", "point": 1e-5, "start": "2005-01-01"},
    "XAUUSD": {"instrument": "XAUUSD", "point": 1e-3, "start": "2008-01-01"},
    "XAGUSD": {"instrument": "XAGUSD", "point": 1e-3, "start": "2008-01-01"},
    "NAS100": {"instrument": "USATECHIDXUSD", "point": 1e-3, "start": "2013-01-01"},
}
CCY_PAIR = {"EUR": "EURUSD", "GBP": "GBPUSD", "JPY": "USDJPY", "CAD": "USDCAD", "CHF": "USDCHF", "SEK": "USDSEK"}
ALLOC_ASSET = "ALLOCATION"  # memory key for the allocation family (registrations, runs)


def load_spec(path: str | Path) -> dict[str, Any]:
    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for k in ("name", "kind", "hypothesis", "universe", "variants", "splits", "costs_bps_per_unit_turnover"):
        if not spec.get(k):
            raise ConfigError(f"allocation spec needs '{k}'")
    return spec


def spec_sha256(spec: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(spec, sort_keys=True, default=str).encode()).hexdigest()


def hourly_bars(name: str, end: str = "2026-10-01") -> pd.DataFrame:
    p = INSTRUMENTS[name]
    raw = build_source("dukascopy_candles", {"instrument": p["instrument"], "start": p["start"], "end": end,
                                             "granularity": "hour", "point": p["point"]}).fetch_series()
    bars, rep = clean_bars(raw, tz="America/New_York", timeframe="1h")
    if rep.verdict == "FAIL":
        raise ConfigError(f"{name}: data quality FAIL {rep.notes}")
    return bars


def daily_panel(names: list[str]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    hourly = {n: hourly_bars(n) for n in names}
    closes = {n: aggregate_sessions(b, "17:00", "America/New_York", 12)[0]["close"] for n, b in hourly.items()}
    return pd.DataFrame(closes).sort_index(), hourly


def portfolio_returns(weights: pd.DataFrame, rets: pd.DataFrame, cost_bps: dict[str, float]) -> pd.DataFrame:
    w = weights.reindex(rets.index).fillna(0.0)
    gross = (w.shift(1) * rets.fillna(0.0)).sum(axis=1)
    turnover = w.diff().abs().fillna(w.abs())
    costs = (turnover * pd.Series(cost_bps)[w.columns] * 1e-4).sum(axis=1).shift(1).fillna(0.0)
    return pd.DataFrame({"gross": gross, "cost": costs, "net": gross - costs,
                         "exposure": w.abs().sum(axis=1), "turnover": turnover.sum(axis=1)})


def summary(r: pd.Series) -> dict[str, Any]:
    r = r.dropna()
    if len(r) < 20:
        return {"days": int(len(r))}
    eq = (1 + r).cumprod()
    yearly = (1 + r).groupby(pd.DatetimeIndex(r.index).year).prod() - 1
    return {"days": int(len(r)), "ann_return": float(np.prod(1 + r.to_numpy())) ** (252 / len(r)) - 1,
            "ann_vol": float(r.std() * math.sqrt(252)), "sharpe": float(sharpe(r.to_numpy(), 252)),
            "max_drawdown": float((1 - eq / eq.cummax()).max()), "profitable_years": float((yearly > 0).mean()),
            "yearly": {int(y): round(float(v), 4) for y, v in zip(yearly.index.to_numpy(), yearly.to_numpy(), strict=True)}}


def boot_sharpe(r: np.ndarray, reps: int, rng: np.random.Generator, bench: np.ndarray | None = None) -> dict[str, float]:
    vals = []
    for _ in range(reps):
        i = stationary_bootstrap_indices(len(r), 20.0, rng)
        vals.append(sharpe(r[i], 252) - (sharpe(bench[i], 252) if bench is not None else 0.0))
    v = np.asarray(vals)
    return {"lo": float(np.quantile(v, 0.025)), "hi": float(np.quantile(v, 0.975)), "p_le_0": float(np.mean(v <= 0))}


class AllocationStudy:
    def __init__(self, spec: dict[str, Any], memory: ResearchMemory, offline: bool = True, seed: int = 7,
                 reps: int = 2000, panel: tuple[pd.DataFrame, dict[str, pd.DataFrame]] | None = None) -> None:
        self.spec, self.memory, self.offline, self.panel = spec, memory, offline, panel
        self.sha = spec_sha256(spec)
        self.rng = np.random.default_rng(seed)
        self.reps = reps
        self.guard = SplitGuard()

    def _weights(self, closes: pd.DataFrame, rets: pd.DataFrame, hourly: dict[str, pd.DataFrame],
                 v: dict[str, Any], train: pd.Series) -> tuple[pd.DataFrame, dict[str, Any]]:
        kind = self.spec["kind"]
        if kind == "vol_managed":
            name = self.spec["universe"][0]
            hr = np.log(hourly[name]["close"]).diff() if name in hourly else None
            w, info = rules.vol_managed(rets[name], hr, v["rv"], int(v["window"]), float(v["cap"]), train)
            return w.to_frame(name), info
        if kind == "tsmom":
            return rules.tsmom(closes, int(v["lookback"])), {}
        if kind == "xs_momentum":
            return rules.xs_momentum(closes, int(v["lookback"])), {}
        raise ConfigError(f"unknown allocation kind {kind}")

    def run(self) -> dict[str, Any]:
        spec = self.spec
        prior = self.memory.registration(spec["name"], ALLOC_ASSET)
        if prior and prior["sha256"] != self.sha:
            raise ConfigError(f"allocation spec '{spec['name']}' was registered with different content; register a new name")
        if prior and prior.get("run_id"):
            raise ConfigError(f"allocation spec '{spec['name']}' already evaluated in {prior['run_id']} ({prior['verdict']})")
        if self.panel is not None:  # injected data (tests)
            closes, hourly = self.panel
        elif spec["kind"] == "xs_momentum":
            pairs, hourly = daily_panel([CCY_PAIR[c] for c in spec["universe"]])
            orient = spec.get("fx_orientation") or {}
            closes = pd.DataFrame({c: pairs[CCY_PAIR[c]] ** orient.get(CCY_PAIR[c], 1) for c in spec["universe"]})
        else:
            closes, hourly = daily_panel(list(spec["universe"]))
        dv = hashlib.sha256(pd.util.hash_pandas_object(closes.fillna(-1)).to_numpy().tobytes()).hexdigest()[:16]
        if not prior:
            self.memory.register(spec["name"], ALLOC_ASSET, dv, self.sha, spec, len(spec["variants"]), [])
        run_id = self.memory.start_run(ALLOC_ASSET, "allocation", dv, self.sha[:16], 0)
        n_family = self.memory.registered_variants(ALLOC_ASSET)
        # each instrument's return over ITS previous session (a holiday gap is one return, not a lost day)
        rets = closes.apply(lambda s: s.dropna().pct_change()).reindex(closes.index)
        idx = pd.DatetimeIndex(closes.index).tz_convert("America/New_York").tz_localize(None)
        sp = spec["splits"]
        cut = {k: pd.Timestamp(sp[k]) + pd.Timedelta(days=1) for k in ("train_end", "validation_end", "test_end")}
        split = pd.Series(np.select([idx < cut["train_end"], idx < cut["validation_end"], idx < cut["test_end"]],
                                    ["train", "validation", "test"], "final"), index=closes.index)
        train = split == "train"
        primary = split.isin(["train", "validation"])
        costs = {k: float(v) for k, v in spec["costs_bps_per_unit_turnover"].items()}
        results = []
        for v in spec["variants"]:
            w, info = self._weights(closes, rets, hourly, v, train)
            pr = portfolio_returns(w, rets[w.columns], costs)
            started = pr["exposure"].gt(0).cummax().shift(1).fillna(False).astype(bool)  # skip the warm-up
            net = pr["net"][started]
            res: dict[str, Any] = {"variant": v, "info": info,
                                   "primary": summary(net[primary]), "train": summary(net[train]),
                                   "validation": summary(net[split == "validation"]),
                                   "avg_exposure": float(pr["exposure"][started & primary].mean()),
                                   "turnover_per_year": float(pr["turnover"][started & primary].sum()
                                                              / max(primary[started].sum() / 252, 1e-9)),
                                   "cost_drag_per_year": float(pr["cost"][started & primary].mean() * 252),
                                   "gross_primary_sharpe": float(sharpe(pr["gross"][started & primary].to_numpy(), 252))}
            r = net[primary].to_numpy()
            res["bootstrap"] = boot_sharpe(r, self.reps, self.rng)
            res["deflated_sharpe"] = deflated_sharpe_report(r, n_family, 0.0, 252)
            checks = {"sharpe_positive": res["primary"].get("sharpe", -1) > 0,
                      "deflated_sharpe": res["deflated_sharpe"]["dsr"] >= 0.95,
                      "profitable_years": res["primary"].get("profitable_years", 0) >= 0.5}
            if spec["kind"] == "vol_managed":
                name = spec["universe"][0]
                bench = rets[name][started].fillna(0.0)
                b = bench[primary].to_numpy()
                res["benchmark_primary"] = summary(bench[primary])
                res["bootstrap_vs_benchmark"] = boot_sharpe(r, self.reps, self.rng, bench=b)
                checks["beats_benchmark"] = (res["primary"].get("sharpe", -9) > res["benchmark_primary"].get("sharpe", 9)
                                             and res["bootstrap_vs_benchmark"]["p_le_0"] < 0.05)
            else:
                checks["bootstrap_ci_above_0"] = res["bootstrap"]["lo"] > 0
            res["checks"] = checks
            res["status"] = "PASSED_PRIMARY" if all(checks.values()) else "REJECTED"
            res["_net"], res["_bench"] = net, (rets[spec["universe"][0]][started].fillna(0.0)
                                               if spec["kind"] == "vol_managed" else None)
            results.append(res)
        for res in [x for x in results if x["status"] == "PASSED_PRIMARY"]:
            self.guard.request("test", "evaluate", f"allocation:{spec['name']}:{res['variant']}")
            t = res["_net"][split == "test"]
            res["test"] = summary(t)
            ok = res["test"].get("sharpe", -1) > 0
            if spec["kind"] == "vol_managed":
                bt = res["_bench"][split == "test"]
                res["test_benchmark"] = summary(bt)
                ok = ok and res["test"].get("sharpe", -9) > res["test_benchmark"].get("sharpe", 9)
            res["status"] = "ROBUST" if ok else "REJECTED"
        robust = sorted([x for x in results if x["status"] == "ROBUST"], key=lambda x: -x["primary"]["sharpe"])
        verdict = "NO EDGE FOUND"
        if robust:
            top = robust[0]
            self.guard.request("final", "evaluate", f"allocation:{spec['name']}:{top['variant']}")
            top["final"] = summary(top["_net"][split == "final"])
            fin_ok = top["final"].get("sharpe", -1) > 0
            if spec["kind"] == "vol_managed":
                top["final_benchmark"] = summary(top["_bench"][split == "final"])
                fin_ok = fin_ok and top["final"].get("sharpe", -9) > top["final_benchmark"].get("sharpe", 9)
            verdict = "EDGE FOUND (provisional)" if fin_ok else "NO EDGE FOUND"
        for res in results:
            res.pop("_net"), res.pop("_bench")
        out = {"run_id": run_id, "spec": spec, "sha256": self.sha, "dataset_version": dv, "multiple_testing_n": n_family,
               "data": {"instruments": list(closes.columns), "start": str(closes.index[0]), "end": str(closes.index[-1]),
                        "first_valid": {c: str(closes[c].first_valid_index()) for c in closes.columns}},
               "splits": {k: str(v) for k, v in sp.items()}, "results": results, "verdict": verdict,
               "split_access": list(self.guard.log)}
        self.memory.record_split_access(run_id, self.guard.log)
        self.memory.complete_registration(spec["name"], ALLOC_ASSET, run_id, verdict)
        self.memory.update_run(run_id, status="FINISHED", verdict=verdict, finished_at=pd.Timestamp.now(tz="UTC").isoformat(),
                               summary={"detail": f"allocation '{spec['name']}': "
                                                  + ", ".join(f"{r['variant']} -> {r['status']}" for r in results)})
        return out


def write_report(out: dict[str, Any], out_dir: Path | None = None) -> tuple[Path, Path]:
    out_dir = out_dir or PROJECT_ROOT / "research_output" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    s = out["spec"]
    f = lambda x, p=False: "n/a" if x is None or (isinstance(x, float) and not math.isfinite(x)) else (  # noqa: E731
        f"{x:.2%}" if p else f"{x:.2f}")
    L = ["# X-QUANT ALLOCATION STUDY (pre-registered)", "", f"> **VERDICT: {out['verdict']}**", "",
         "Research/backtest output only. Not investment advice. No live trading.", "",
         f"**{s['name']}** ({s['kind']}) - run {out['run_id']}, spec sha256 `{out['sha256']}`, "
         f"multiple-testing N = {out['multiple_testing_n']}", "", f"> {s['hypothesis']}", "",
         f"Rationale: {s.get('rationale', '')}", "", f"Rules: {s.get('rules', '')}", "",
         f"Pass rule: {s.get('pass_rule', '')}", "",
         f"Data: {out['data']['instruments']} daily sessions (17:00 NY) {out['data']['start']} .. {out['data']['end']}; "
         f"first valid {out['data']['first_valid']}", f"Splits: {out['splits']}", "",
         "| Variant | Status | Primary Sharpe (net) | gross | CAGR | Vol | Max DD | Profitable years | Bootstrap 95% CI | DSR | Turnover/yr | Cost drag/yr |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["results"]:
        p, b = r["primary"], r["bootstrap"]
        L.append(f"| {r['variant']} | {r['status']} | {f(p.get('sharpe'))} | {f(r['gross_primary_sharpe'])} | "
                 f"{f(p.get('ann_return'), True)} | {f(p.get('ann_vol'), True)} | {f(p.get('max_drawdown'), True)} | "
                 f"{f(p.get('profitable_years'), True)} | {f(b['lo'])}..{f(b['hi'])} | {f(r['deflated_sharpe']['dsr'])} | "
                 f"{f(r['turnover_per_year'])} | {f(r['cost_drag_per_year'], True)} |")
    for r in out["results"]:
        L += ["", f"### {r['variant']} - {r['status']}", "", f"- checks: {r['checks']}"]
        if "benchmark_primary" in r:
            bp = r["benchmark_primary"]
            L.append(f"- buy-and-hold on the same days: Sharpe {f(bp.get('sharpe'))}, CAGR {f(bp.get('ann_return'), True)}, "
                     f"vol {f(bp.get('ann_vol'), True)}, max DD {f(bp.get('max_drawdown'), True)}; Sharpe difference "
                     f"bootstrap 95% CI {f(r['bootstrap_vs_benchmark']['lo'])}..{f(r['bootstrap_vs_benchmark']['hi'])}, "
                     f"P(diff<=0) {f(r['bootstrap_vs_benchmark']['p_le_0'])}")
        L.append(f"- TRAIN Sharpe {f(r['train'].get('sharpe'))}, VALIDATION Sharpe {f(r['validation'].get('sharpe'))}; "
                 f"average gross exposure {f(r['avg_exposure'])}; {r.get('info') or ''}")
        L.append(f"- yearly net returns: {r['primary'].get('yearly')}")
        for k in ("test", "final"):
            if k in r:
                L.append(f"- {k.upper()}: Sharpe {f(r[k].get('sharpe'))}, CAGR {f(r[k].get('ann_return'), True)}")
    L += ["", "## Protected split access", ""] + ([f"- {e['split']}/{e['purpose']}: {e['who']}" for e in out["split_access"]]
                                                  or ["- none (no variant passed the primary sample)"])
    L += ["", "## Limitations", "",
          "- Daily sessions from Dukascopy CFD/FX mid prices; tick volume only; no risk-free rate (excess returns not computed).",
          "- Weights held constant between rebalances; costs = turnover x fixed cost per unit (no market impact model).", ""]
    md = out_dir / f"{out['run_id']}_ALLOC_{s['name']}.md"
    js = out_dir / f"{out['run_id']}_ALLOC_{s['name']}.json"
    md.write_text("\n".join(L), encoding="utf-8")
    js.write_text(json.dumps(out, default=str, separators=(",", ":")), encoding="utf-8")
    return md, js
