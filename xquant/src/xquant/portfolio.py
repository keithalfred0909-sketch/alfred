"""PORTFOLIO VIEW: combine VALIDATED strategies (any asset) and measure frequency at the portfolio level.

A trading-frequency requirement ("at least one trade per day") is a property of the book, not of every
strategy: demanding it per strategy discards slow edges that could add up. Only strategies that survived
everything (status ROBUST) are eligible - combining rejected near-misses is a classic way to manufacture a
backtest, so it is not offered.

Return correlation and the combined Sharpe are approximations from the stored equity curves (~400 points
over TRAIN+VALIDATION, equal weights); trades per day come from the VALIDATION split of each strategy.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from xquant.memory.store import ResearchMemory, unpack

ELIGIBLE = ("ROBUST",)


def portfolio_view(mem: ResearchMemory, min_trades_per_day: float = 0.0) -> dict[str, Any]:
    comps: list[dict[str, Any]] = []
    curves: dict[str, pd.Series] = {}
    for r in mem.query("SELECT id, asset, status, description, dossier FROM strategies WHERE status IN "
                       f"({','.join('?' * len(ELIGIBLE))})", ELIGIBLE):
        d = unpack(r["dossier"], {})
        v = d.get("validation") or {}
        years = v.get("years") or 0.0
        per_day = (v.get("trades") or 0) / (years * 252) if years else math.nan
        comps.append({"id": r["id"], "asset": r["asset"], "rules": r["description"], "val_sharpe": v.get("sharpe"),
                      "val_trades": v.get("trades"), "trades_per_day": per_day})
        eq = d.get("equity") or {}
        if eq.get("dates") and eq.get("combined"):
            curves[r["id"]] = pd.Series(eq["combined"], index=pd.to_datetime(eq["dates"])).groupby(level=0).last()
    out: dict[str, Any] = {"components": comps, "eligible_status": list(ELIGIBLE),
                           "required_trades_per_day": min_trades_per_day}
    if not comps:
        out["verdict"] = ("NO PORTFOLIO: no strategy has been validated yet (status ROBUST). A portfolio can only be "
                          "built from validated components; the frequency requirement cannot be assessed.")
        return out
    out["portfolio_trades_per_day"] = float(np.nansum([c["trades_per_day"] for c in comps]))
    if len(curves) >= 2:
        # equity is cumulative log-return style P&L per unit notional: differences = period returns
        rets = pd.DataFrame(curves).sort_index().ffill().diff().dropna(how="all").fillna(0.0)
        corr = rets.corr()
        out["correlation"] = corr.round(3).to_dict()
        port = rets.mean(axis=1)
        if port.std() > 0:
            per_year = len(port) / max((port.index[-1] - port.index[0]).days / 365.25, 1e-9)
            out["approx_portfolio_sharpe"] = float(port.mean() / port.std() * math.sqrt(per_year))
    meets = out["portfolio_trades_per_day"] >= min_trades_per_day
    out["verdict"] = (f"{len(comps)} validated component(s); {out['portfolio_trades_per_day']:.2f} trades/day "
                      f"({'meets' if meets else 'below'} the {min_trades_per_day:g}/day requirement)")
    return out


def format_view(v: dict[str, Any]) -> str:
    L = [f"PORTFOLIO (eligible status: {', '.join(v['eligible_status'])})", v["verdict"]]
    for c in v["components"]:
        L.append(f"  {c['id']} [{c['asset']}] val SR {c['val_sharpe']}, {c['val_trades']} trades, "
                 f"{c['trades_per_day']:.2f}/day - {c['rules']}")
    if "approx_portfolio_sharpe" in v:
        L.append(f"approx. equal-weight Sharpe (from stored equity curves): {v['approx_portfolio_sharpe']:.2f}")
    return "\n".join(L)
