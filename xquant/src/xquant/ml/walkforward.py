"""Pre-registered walk-forward machine-learning study (spec configs/preregistered/ml_gbm_walkforward_v1.yaml).

Every prediction for calendar year Y comes from a model fitted only on bars that end at least ``horizon`` bars
before 1 January of Y (purge: their labels are fully known before Y starts). Trading thresholds are the 10th /
90th percentiles of that model's in-sample probabilities. Evaluation follows the lab contract: primary sample =
walk-forward predictions inside TRAIN+VALIDATION; TEST once for passing assets; FINAL once for the best.
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

from xquant.backtest.engine import MarketArrays, run_backtest
from xquant.config import PROJECT_ROOT, CostModel, load_config
from xquant.errors import ConfigError
from xquant.features.library import build_primitives
from xquant.market.behavior import periods_per_year
from xquant.memory.store import ResearchMemory
from xquant.stats import sharpe, stationary_bootstrap_indices
from xquant.validation.overfit import deflated_sharpe_report
from xquant.validation.robustness import stressed_costs
from xquant.validation.splits import SplitGuard, make_splits

FAMILY = "ML"


def load_spec(path: str | Path) -> dict[str, Any]:
    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for k in ("name", "assets", "model"):
        if not spec.get(k):
            raise ConfigError(f"ML spec needs '{k}'")
    return spec


def spec_sha256(spec: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(spec, sort_keys=True, default=str).encode()).hexdigest()


def walk_forward_predictions(X: pd.DataFrame, y: pd.Series, local_years: np.ndarray, horizon: int,
                             model_params: dict[str, Any], first_year: int) -> pd.DataFrame:
    """Columns p, hi, lo (NaN where no model existed yet)."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    params = {k: v for k, v in model_params.items() if k != "class"}
    out = pd.DataFrame(np.nan, index=X.index, columns=["p", "hi", "lo"])
    Xv = X.to_numpy(dtype=float)
    yv = y.to_numpy(dtype=float)
    for year in range(first_year, int(local_years.max()) + 1):
        start = int(np.searchsorted(local_years, year, side="left"))
        stop = int(np.searchsorted(local_years, year, side="right"))
        if stop <= start:
            continue
        tr_end = max(start - horizon, 0)  # purge: labels of training rows end before the year starts
        mask = np.isfinite(yv[:tr_end])
        if mask.sum() < 1000:
            continue
        Xt = Xv[:tr_end][mask]
        cols = np.flatnonzero(np.isfinite(Xt).sum(axis=0) >= 100)  # features with data in this training window
        model = HistGradientBoostingClassifier(**params)
        model.fit(Xt[:, cols], yv[:tr_end][mask].astype(int))
        p_in = model.predict_proba(Xt[:, cols])[:, 1]
        out.iloc[start:stop, 0] = model.predict_proba(Xv[start:stop][:, cols])[:, 1]
        out.iloc[start:stop, 1] = float(np.quantile(p_in, 0.9))
        out.iloc[start:stop, 2] = float(np.quantile(p_in, 0.1))
    return out


def combined_returns(m: MarketArrays, pred: pd.DataFrame, costs: CostModel, window: slice, hold: int) -> tuple[pd.Series, int]:
    p, hi, lo = (pred[c].to_numpy() for c in ("p", "hi", "lo"))
    with np.errstate(invalid="ignore"):
        long_e, short_e = np.nan_to_num(p >= hi).astype(bool), np.nan_to_num(p <= lo).astype(bool)
    rl = run_backtest(m, long_e, 1, hold, None, None, costs, window)
    rs = run_backtest(m, short_e, -1, hold, None, None, costs, window)
    return rl.returns + rs.returns, int(rl.metrics.trades + rs.metrics.trades)


def summarize(r: pd.Series, ppy: float, trades: int) -> dict[str, Any]:
    r = r.dropna()
    if len(r) < 50:
        return {"bars": int(len(r)), "trades": trades}
    years = r.groupby(pd.DatetimeIndex(r.index).year).sum()
    return {"bars": int(len(r)), "trades": trades, "sharpe": float(sharpe(r.to_numpy(), ppy)),
            "ann_return": float(r.mean() * ppy), "profitable_years": float((years > 0).mean()),
            "yearly": {int(k): round(float(v), 4) for k, v in zip(years.index.to_numpy(), years.to_numpy(), strict=True)}}


class MLStudy:
    def __init__(self, spec: dict[str, Any], memory: ResearchMemory, offline: bool = True, seed: int = 13,
                 reps: int = 1000, datasets: dict[str, tuple[pd.DataFrame, pd.DataFrame, Any]] | None = None) -> None:
        self.spec, self.memory, self.offline, self.datasets = spec, memory, offline, datasets
        self.sha = spec_sha256(spec)
        self.rng = np.random.default_rng(seed)
        self.reps = reps
        self.guard = SplitGuard()

    def _data(self, asset: str) -> tuple[pd.DataFrame, pd.DataFrame, Any]:
        if self.datasets and asset in self.datasets:
            return self.datasets[asset]
        from xquant.data.engine import DataEngine
        cfg = load_config(asset)
        ds = DataEngine(cfg.asset, offline=self.offline).load()
        return ds.bars, ds.exog, cfg

    def run(self) -> dict[str, Any]:
        spec, horizon = self.spec, 6
        prior = self.memory.registration(spec["name"], FAMILY)
        if prior and prior["sha256"] != self.sha:
            raise ConfigError(f"ML spec '{spec['name']}' was registered with different content; register a new version")
        if prior and prior.get("run_id"):
            raise ConfigError(f"ML spec '{spec['name']}' already evaluated in {prior['run_id']} ({prior['verdict']})")
        if not prior:
            self.memory.register(spec["name"], FAMILY, "multi", self.sha, spec, len(spec["assets"]), [])
        run_id = self.memory.start_run(FAMILY, "ml", "multi", self.sha[:16], 0)
        n_family = self.memory.registered_variants(FAMILY)
        results = []
        for asset in spec["assets"]:
            bars, exog, cfg = self._data(asset)
            tz = cfg.asset.timezone
            prims = build_primitives(bars, exog.reindex(bars.index) if exog is not None and not exog.empty else None, tz)
            X = pd.DataFrame(prims).replace([np.inf, -np.inf], np.nan)
            lc = np.log(bars["close"])
            fwd = lc.shift(-horizon) - lc
            y = (fwd > 0).astype(float).where(fwd.notna())
            years = np.asarray(pd.DatetimeIndex(bars.index).tz_convert(tz).year)
            first_year = int(years.min()) + 3 + (0 if pd.DatetimeIndex(bars.index).tz_convert(tz)[0].dayofyear <= 7 else 1)
            pred = walk_forward_predictions(X, y, years, horizon, spec["model"], first_year)
            splits = make_splits(pd.DatetimeIndex(bars.index), cfg.asset.splits)
            ppy = periods_per_year(pd.DatetimeIndex(bars.index))
            m = MarketArrays.from_bars(bars, ppy)
            first = int(np.flatnonzero(pred["p"].notna().to_numpy())[0])
            prim = slice(first, splits.slice("validation").stop)
            r, n_tr = combined_returns(m, pred, cfg.asset.costs, prim, horizon)
            r2, _ = combined_returns(m, pred, stressed_costs(cfg.asset.costs, 2.0), prim, horizon)
            res: dict[str, Any] = {"asset": asset, "first_prediction": str(bars.index[first]),
                                   "primary": summarize(r, ppy, n_tr), "cost_x2": summarize(r2, ppy, n_tr),
                                   "n_features": int(X.shape[1])}
            rv = r.to_numpy()
            boots = [sharpe(rv[stationary_bootstrap_indices(len(rv), 120.0, self.rng)], ppy) for _ in range(self.reps)]
            res["sharpe_ci"] = [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]
            res["deflated_sharpe"] = deflated_sharpe_report(rv, n_family, 0.0, ppy)
            res["checks"] = {"sharpe_ci_above_0": bool(res["sharpe_ci"][0] > 0),
                             "deflated_sharpe": bool(res["deflated_sharpe"]["dsr"] >= 0.95),
                             "profitable_years": bool(res["primary"].get("profitable_years", 0) >= 0.5),
                             "cost_x2_positive": bool(res["cost_x2"].get("sharpe", -1) > 0)}
            res["status"] = "PASSED_PRIMARY" if all(res["checks"].values()) else "REJECTED"
            if res["status"] == "PASSED_PRIMARY":
                self.guard.request("test", "evaluate", f"ml:{spec['name']}:{asset}")
                rt, nt = combined_returns(m, pred, cfg.asset.costs, splits.slice("test"), horizon)
                res["test"] = summarize(rt, ppy, nt)
                res["status"] = "ROBUST" if res["test"].get("sharpe", -1) > 0 else "REJECTED"
                res["_final"] = (m, pred, cfg.asset.costs, splits.slice("final"), ppy)
            results.append(res)
        robust = sorted([x for x in results if x["status"] == "ROBUST"], key=lambda x: -x["primary"]["sharpe"])
        verdict = "NO EDGE FOUND"
        if robust:
            top = robust[0]
            m, pred, costs, fin, ppy = top["_final"]
            self.guard.request("final", "evaluate", f"ml:{spec['name']}:{top['asset']}")
            rf, nf = combined_returns(m, pred, costs, fin, horizon)
            top["final"] = summarize(rf, ppy, nf)
            verdict = "EDGE FOUND (provisional)" if top["final"].get("sharpe", -1) > 0 else "NO EDGE FOUND"
        for x in results:
            x.pop("_final", None)
        out = {"run_id": run_id, "spec": spec, "sha256": self.sha, "multiple_testing_n": n_family, "results": results,
               "verdict": verdict, "split_access": list(self.guard.log)}
        self.memory.record_split_access(run_id, self.guard.log)
        self.memory.complete_registration(spec["name"], FAMILY, run_id, verdict)
        self.memory.update_run(run_id, status="FINISHED", verdict=verdict, finished_at=pd.Timestamp.now(tz="UTC").isoformat(),
                               summary={"detail": f"ML '{spec['name']}': " + ", ".join(f"{x['asset']} -> {x['status']}" for x in results)})
        return out


def write_report(out: dict[str, Any], out_dir: Path | None = None) -> tuple[Path, Path]:
    out_dir = out_dir or PROJECT_ROOT / "research_output" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    s = out["spec"]

    def f(x: Any, pct: bool = False) -> str:
        if x is None or (isinstance(x, float) and not math.isfinite(x)):
            return "n/a"
        return f"{x:.2%}" if pct else f"{x:.2f}"
    L = ["# X-QUANT ML WALK-FORWARD STUDY (pre-registered)", "", f"> **VERDICT: {out['verdict']}**", "",
         "Research/backtest output only. Not investment advice. No live trading.", "",
         f"**{s['name']}** - run {out['run_id']}, spec sha256 `{out['sha256']}`, multiple-testing N = {out['multiple_testing_n']}",
         "", f"> {s['hypothesis']}", "", f"Model: {s['model']}", f"Walk-forward: {s['walk_forward']}",
         f"Trading rule: {s['trading_rule']}", f"Pass rule: {s['pass_rule']}", "",
         "| Asset | Status | First prediction | Trades | Sharpe (95% CI) | Ann. return | Profitable years | Sharpe at 2x costs | DSR |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in out["results"]:
        p = r["primary"]
        L.append(f"| {r['asset']} | {r['status']} | {r['first_prediction'][:10]} | {p.get('trades')} | {f(p.get('sharpe'))} "
                 f"({f(r['sharpe_ci'][0])}..{f(r['sharpe_ci'][1])}) | {f(p.get('ann_return'), True)} | "
                 f"{f(p.get('profitable_years'), True)} | {f(r['cost_x2'].get('sharpe'))} | {f(r['deflated_sharpe']['dsr'])} |")
    for r in out["results"]:
        L += ["", f"### {r['asset']} - {r['status']}", f"- checks: {r['checks']}", f"- yearly: {r['primary'].get('yearly')}"]
        for k in ("test", "final"):
            if k in r:
                L.append(f"- {k.upper()}: Sharpe {f(r[k].get('sharpe'))}, {r[k].get('trades')} trades")
    L += ["", "## Protected split access", ""] + ([f"- {e['split']}/{e['purpose']}: {e['who']}" for e in out["split_access"]]
                                                  or ["- none (no asset passed the primary sample)"])
    md = out_dir / f"{out['run_id']}_ML_{s['name']}.md"
    js = out_dir / f"{out['run_id']}_ML_{s['name']}.json"
    md.write_text("\n".join(L), encoding="utf-8")
    js.write_text(json.dumps(out, default=str, separators=(",", ":")), encoding="utf-8")
    return md, js
