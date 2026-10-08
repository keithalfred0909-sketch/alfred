"""MACRO INTELLIGENCE ENGINE.

Two families of questions:

* Macro *state* -> subsequent price behaviour. Uses point-in-time macro/cross-asset series (levels and
  changes) bucketed with TRAIN quantiles; HAC tests; BH within the batch; replication on VALIDATION.
* Macro *events* (releases with expectations) -> reaction / drift, via ``event_study``. Requires an
  economic calendar with consensus; without it every event question is INSUFFICIENT DATA.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from xquant.data.engine import MarketDataset
from xquant.findings import Finding, apply_fdr, replicate
from xquant.logging_utils import get_logger
from xquant.macro.event_study import event_study
from xquant.macro.expectation import compute_surprises
from xquant.stats import TestResult, forward_returns, hac_conditional_diff
from xquant.validation.splits import DataSplits

log = get_logger("macro")
ENGINE = "macro"

CORE_EVENTS = ["CPI", "PCE", "NFP", "Unemployment rate", "Average hourly earnings", "GDP", "PMI",
               "Fed rate decision", "ECB rate decision", "Central bank statements"]


def macro_state_frame(exog: pd.DataFrame, change_bars: int = 63) -> pd.DataFrame:
    """Levels and changes of every exogenous series (already point-in-time aligned)."""
    cols = {}
    for c in exog.columns:
        s = exog[c]
        cols[f"{c}"] = s
        cols[f"{c}_chg{change_bars}"] = s - s.shift(change_bars)
    return pd.DataFrame(cols, index=exog.index)


class MacroEngine:
    def __init__(self, ds: MarketDataset, splits: DataSplits, regimes: pd.Series | None = None) -> None:
        self.ds, self.splits, self.regimes = ds, splits, regimes
        self.lc = np.log(ds.bars["close"])
        self.train = splits.mask("train").to_numpy()
        self.val = splits.mask("validation").to_numpy()

    def state_tests(self, horizons: tuple[int, ...] = (5, 20)) -> list[tuple[Finding, Callable[[np.ndarray], TestResult]]]:
        if self.ds.exog.empty:
            return []
        state = macro_state_frame(self.ds.exog)
        out: list[tuple[Finding, Callable[[np.ndarray], TestResult]]] = []
        span = "{} to {}".format(*self.splits.span("train"))
        for col in state.columns:
            x = state[col]
            if x[self.train].notna().sum() < 300:
                continue
            for side, q in [("low", 0.2), ("high", 0.8)]:
                thr = float(x[self.train].quantile(q))
                cond = (x < thr) if side == "low" else (x > thr)
                for h in horizons:
                    y = forward_returns(self.lc, h).to_numpy()
                    cv = cond.fillna(False).to_numpy(dtype=bool)

                    def fn(mask: np.ndarray, y: np.ndarray = y, cv: np.ndarray = cv, h: int = h) -> TestResult:
                        return hac_conditional_diff(y[mask], cv[mask], lags=h)
                    f = Finding.from_test(ENGINE, "macro_state", f"{col}_{side}20_fwd{h}",
                                          f"next {h}-bar {self.ds.meta.symbol} return when {col} is in its {side} quintile (train thresholds)",
                                          fn(self.train), span, threshold=thr)
                    out.append((f, fn))
        return out

    def event_findings(self) -> list[Finding]:
        ev = self.ds.events
        if ev is None or ev.empty:
            return [Finding.insufficient(ENGINE, "event_study", name,
                                         "no economic calendar with timestamps/consensus connected "
                                         "(configure asset.calendar_source)") for name in CORE_EVENTS]
        ev = compute_surprises(ev)
        out: list[Finding] = []
        span = "{} to {}".format(*self.splits.span("train"))
        for name, g in ev.groupby("event"):
            out += event_study(g, self.ds.bars["close"], self.train, str(name), ENGINE, span, regimes=self.regimes)
        return out

    def run(self, fdr_alpha: float = 0.05) -> list[Finding]:
        pairs = self.state_tests()
        tested = [f for f, _ in pairs]
        fns = {f.name: fn for f, fn in pairs}
        for f in tested:
            if not np.isfinite(f.p_value):
                f.status = "INSUFFICIENT DATA"
        events = self.event_findings()
        ev_tested = [f for f in events if f.status == "TESTED"]
        apply_fdr(tested + ev_tested, fdr_alpha)
        replicate(tested, lambda f: fns[f.name](self.val), fdr_alpha)
        for f in ev_tested:  # event findings: replication would need a validation-window event study
            if f.status == "SIGNIFICANT_TRAIN":
                f.status = "SIGNIFICANT_TRAIN (replication pending)"
        notes = [Finding.descriptive(ENGINE, "data", "macro_data_limits",
                                     "Macro series are latest-vintage (revised) values with conservative publication lags; "
                                     "no consensus data => no surprise analysis", "",
                                     series={k: {kk: v.get(kk) for kk in ("status", "lag_days", "frequency", "description")}
                                             for k, v in self.ds.exog_meta.items()})]
        log.info("macro: %d state tests, %d discoveries; %d event findings", len(tested),
                 sum(f.status == "DISCOVERY" for f in tested), len(events))
        return notes + tested + events
