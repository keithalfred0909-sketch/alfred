"""MARKET BEHAVIOR ENGINE: exploratory statistics of the asset before any strategy exists.

Every question is a ``BehaviorTest``: a function of a boolean mask that returns a TestResult. Tests run
on TRAIN, are BH-corrected as one batch, and significant ones are re-run on VALIDATION. Questions the
data cannot answer (intraday timing on daily bars, gaps without opens, volume without volume) are
reported as INSUFFICIENT DATA rather than skipped silently.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as sps

from xquant.data.engine import MarketDataset
from xquant.findings import Finding, apply_fdr, replicate
from xquant.logging_utils import get_logger
from xquant.market.regimes import RegimeModel, fit_regimes
from xquant.stats import (
    NAN_RESULT,
    TestResult,
    arch_lm,
    forward_returns,
    hac_conditional_diff,
    hac_mean_test,
    ljung_box,
    runs_test,
    variance_ratio_test,
)
from xquant.validation.splits import DataSplits

log = get_logger("market")
ENGINE = "market"


@dataclass
class BehaviorTest:
    category: str
    name: str
    description: str
    fn: Callable[[np.ndarray], TestResult]  # boolean mask over bars -> result


def periods_per_year(index: pd.DatetimeIndex) -> float:
    years = (index[-1] - index[0]).days / 365.25
    return len(index) / years if years > 0 else 252.0


class MarketBehaviorEngine:
    def __init__(self, ds: MarketDataset, splits: DataSplits, horizons: list[int], seed: int = 0,
                 tz: str = "UTC") -> None:
        self.ds, self.splits, self.horizons, self.seed, self.tz = ds, splits, horizons, seed, tz
        c = ds.bars["close"]
        self.lc = np.log(c)
        self.r = self.lc.diff()
        self.vol20 = self.r.rolling(20, min_periods=15).std()
        self.vol60 = self.r.rolling(60, min_periods=40).std()
        self.ppy = periods_per_year(pd.DatetimeIndex(c.index))
        self.fwd = {h: forward_returns(self.lc, h) for h in sorted(set(horizons) | {1})}
        self.train_mask = splits.mask("train").to_numpy()
        self.val_mask = splits.mask("validation").to_numpy()
        self.regimes: RegimeModel | None = None

    # ---- helpers -------------------------------------------------------------------------------
    def _q(self, s: pd.Series, q: float) -> float:
        """Quantile threshold estimated on TRAIN only (avoids leaking holdout distribution)."""
        return float(s[self.train_mask].quantile(q))

    def _cond_test(self, y: pd.Series, cond: pd.Series, lags: int) -> Callable[[np.ndarray], TestResult]:
        yv, cv = y.to_numpy(), cond.fillna(False).to_numpy(dtype=bool)

        def fn(mask: np.ndarray) -> TestResult:
            return hac_conditional_diff(yv[mask], cv[mask], lags=lags)
        return fn

    def _signed_mean_test(self, y: pd.Series, cond: pd.Series, lags: int) -> Callable[[np.ndarray], TestResult]:
        yv, cv = y.to_numpy(), cond.fillna(False).to_numpy(dtype=bool)

        def fn(mask: np.ndarray) -> TestResult:
            return hac_mean_test(yv[mask & cv], lags=lags)
        return fn

    # ---- test catalogue ------------------------------------------------------------------------
    def build_tests(self) -> list[BehaviorTest]:
        T: list[BehaviorTest] = []
        r = self.r
        rv = r.to_numpy()

        # Serial dependence: momentum vs reversion at several scales
        for q in [2, 5, 10, 20, 60]:
            def vr(mask: np.ndarray, q: int = q) -> TestResult:
                res = variance_ratio_test(rv[mask], q)
                return TestResult(res.statistic, res.p_value, res.effect - 1.0, res.n) if res.valid else res
            T.append(BehaviorTest("serial_dependence", f"variance_ratio_q{q}",
                                  f"Lo-MacKinlay VR({q}); effect = VR-1 (>0 momentum, <0 mean reversion)", vr))
        T.append(BehaviorTest("serial_dependence", "ljung_box_returns_10",
                              "Ljung-Box(10) on returns; effect = lag-1 autocorrelation",
                              lambda m: ljung_box(rv[m], 10)))

        def runs(mask: np.ndarray) -> TestResult:
            res = runs_test(np.sign(rv[mask][np.isfinite(rv[mask])]))
            return TestResult(res.statistic, res.p_value, res.effect - 1.0, res.n) if res.valid else res
        T.append(BehaviorTest("trend", "runs_test_signs",
                              "Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance", runs))

        # Momentum / trend persistence at several look-backs
        for lb, h in [(20, 5), (60, 20), (120, 20), (250, 20)]:
            mom = np.sign(self.lc - self.lc.shift(lb))
            y = mom * self.fwd[h]
            T.append(BehaviorTest("trend", f"momentum_{lb}_fwd{h}",
                                  f"sign of {lb}-bar return x next {h}-bar return; effect>0 = trend persistence",
                                  self._signed_mean_test(y, mom.notna() & (mom != 0), lags=h)))

        # Reversion after statistical extremes (distance to rolling mean in vol units)
        for w in [20, 60]:
            z = (self.lc - self.lc.rolling(w, min_periods=int(w * 0.75)).mean()) / (
                self.r.rolling(w, min_periods=int(w * 0.75)).std() * np.sqrt(w))
            for side, thr in [("high", self._q(z, 0.95)), ("low", self._q(z, 0.05))]:
                cond = z > thr if side == "high" else z < thr
                for h in [5, 10, 20]:
                    T.append(BehaviorTest("reversion", f"zdist{w}_{side}_fwd{h}",
                                          f"{h}-bar forward return when {w}-bar distance-to-mean z is in the {side} 5% tail (vs rest)",
                                          self._cond_test(self.fwd[h], cond, lags=h)))

        # Large single-bar moves: continuation or reversal
        big = r.abs() > 2.5 * self.vol60.shift(1)
        sgn = np.sign(r)
        for h in [1, 5, 10]:
            T.append(BehaviorTest("extreme_moves", f"big_move_follow_fwd{h}",
                                  f"sign of a >2.5 sigma bar x next {h}-bar return; effect>0 continuation, <0 reversal",
                                  self._signed_mean_test(sgn * self.fwd[h], big, lags=h)))
        T.append(BehaviorTest("extreme_moves", "big_move_clustering",
                              "P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise",
                              self._cond_test(big.shift(-1).astype(float), big, lags=5)))

        # Streaks of consecutive same-sign bars
        streak = self._streaks(r)
        for k in [3, 4, 5]:
            for h in [1, 5]:
                cond = streak.abs() >= k
                T.append(BehaviorTest("sequences", f"streak{k}_fwd{h}",
                                      f"after >={k} consecutive same-sign bars: sign x next {h}-bar return",
                                      self._signed_mean_test(np.sign(streak) * self.fwd[h], cond, lags=h)))

        # Volatility
        T.append(BehaviorTest("volatility", "arch_lm_5", "Engle ARCH-LM(5): volatility clustering; effect = R^2",
                              lambda m: arch_lm(rv[m], 5)))
        T.append(BehaviorTest("volatility", "ljung_box_abs_20", "Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|",
                              lambda m: ljung_box(np.abs(rv[m]), 20)))
        fvol = np.log(self.r.rolling(20).std().shift(-20) / self.vol60)
        vratio = np.log(r.rolling(5, min_periods=4).std() / self.vol60)
        T.append(BehaviorTest("volatility", "compression_then_expansion",
                              "log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest)",
                              self._cond_test(fvol, vratio < self._q(vratio, 0.10), lags=20)))
        T.append(BehaviorTest("volatility", "high_vol_mean_reversion",
                              "log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest)",
                              self._cond_test(fvol, self.vol20 > self._q(self.vol20, 0.90), lags=20)))
        T.append(BehaviorTest("volatility", "vol_level_vs_fwd_return",
                              "next 20-bar return in the top-decile vol20 state (vs rest)",
                              self._cond_test(self.fwd[20], self.vol20 > self._q(self.vol20, 0.90), lags=20)))

        # Calendar / time structure
        idx = pd.DatetimeIndex(self.ds.bars.index).tz_convert(self.tz)
        r_next = self.fwd[1]
        for d, name in enumerate(["mon", "tue", "wed", "thu", "fri"]):
            T.append(BehaviorTest("time", f"weekday_{name}", f"next-bar return when today is {name} (vs other days)",
                                  self._cond_test(r_next, pd.Series(idx.dayofweek == d, index=r.index), lags=1)))
        for mth in range(1, 13):
            T.append(BehaviorTest("time", f"month_{mth:02d}", f"next-bar return in calendar month {mth} (vs others)",
                                  self._cond_test(r_next, pd.Series(idx.month == mth, index=r.index), lags=1)))
        month_id = idx.year * 12 + idx.month
        mid = pd.Series(month_id, index=r.index)
        first = mid != mid.shift(1)
        last = mid != mid.shift(-1)
        T.append(BehaviorTest("time", "turn_of_month_last_bar", "next-bar return from the last bar of the month",
                              self._cond_test(r_next, last, lags=1)))
        T.append(BehaviorTest("time", "turn_of_month_first_bar", "next-bar return from the first bar of the month",
                              self._cond_test(r_next, first, lags=1)))
        if self.ds.meta.capabilities.intraday:
            for hr in range(24):
                cond = pd.Series(idx.hour == hr, index=r.index)
                if cond.sum() > 50:
                    T.append(BehaviorTest("time", f"hour_{hr:02d}", f"next-bar return at hour {hr} (vs other hours)",
                                          self._cond_test(r_next, cond, lags=1)))
        return T

    @staticmethod
    def _streaks(r: pd.Series) -> pd.Series:
        s = np.sign(r.fillna(0)).to_numpy()
        out = np.zeros(len(s))
        for i in range(len(s)):
            if s[i] == 0:
                out[i] = 0
            elif i > 0 and np.sign(out[i - 1]) == s[i]:
                out[i] = out[i - 1] + s[i]
            else:
                out[i] = s[i]
        return pd.Series(out, index=r.index)

    def insufficiency_findings(self) -> list[Finding]:
        caps = self.ds.meta.capabilities
        out = []
        if not caps.intraday:
            for name in ["hour_of_day", "minute", "session_open_close", "intraday_seasonality"]:
                out.append(Finding.insufficient(ENGINE, "time", name,
                                                "daily bars: intraday timing questions cannot be answered"))
        if not caps.ohlc:
            for name in ["atr", "gaps_open_vs_close", "bar_range_structure", "large_candles_body_wick"]:
                out.append(Finding.insufficient(ENGINE, "structure", name,
                                                "close-only data: needs open/high/low (realised close-to-close vol used instead)"))
        if not caps.volume:
            out.append(Finding.insufficient(ENGINE, "liquidity", "volume_liquidity",
                                            "no volume data for this asset/source"))
        return out

    # ---- descriptive -----------------------------------------------------------------------------
    def descriptive(self) -> list[Finding]:
        out = []
        for split in ["train", "validation"]:
            m = self.splits.mask(split).to_numpy()  # type: ignore[arg-type]
            rr = self.r[m].dropna()
            out.append(Finding.descriptive(
                ENGINE, "distribution", f"return_distribution_{split}",
                "Per-bar log return distribution", "{} to {}".format(*self.splits.span(split)),  # type: ignore[arg-type]
                mean_bps=float(rr.mean() * 1e4), ann_vol=float(rr.std() * np.sqrt(self.ppy)),
                skew=float(sps.skew(rr)), excess_kurtosis=float(sps.kurtosis(rr)),
                jarque_bera_p=float(sps.jarque_bera(rr).pvalue), n=int(len(rr))))
        out.append(self._trend_episodes())
        return out

    def _trend_episodes(self) -> Finding:
        """Directional-change episodes with a volatility-scaled threshold; compared with shuffled returns."""
        m = self.train_mask
        rr = self.r[m].dropna().to_numpy()
        thr = 3 * np.nanmedian(self.vol20[m]) * np.sqrt(5)

        def episodes(x: np.ndarray) -> np.ndarray:
            p = np.cumsum(x)
            durs, ext, ext_i, direction, start = [], p[0], 0, 0, 0
            for i in range(1, len(p)):
                if direction >= 0:
                    if p[i] > ext:
                        ext, ext_i = p[i], i
                    elif ext - p[i] > thr:
                        durs.append(ext_i - start)
                        start, direction, ext, ext_i = ext_i, -1, p[i], i
                if direction < 0:
                    if p[i] < ext:
                        ext, ext_i = p[i], i
                    elif p[i] - ext > thr:
                        durs.append(ext_i - start)
                        start, direction, ext, ext_i = ext_i, 1, p[i], i
            return np.array(durs[1:], dtype=float)

        obs = episodes(rr)
        rng = np.random.default_rng(self.seed)
        sims = [episodes(rng.permutation(rr)).mean() for _ in range(200)]
        p = (1 + sum(s >= obs.mean() for s in sims)) / (1 + len(sims))
        return Finding.descriptive(
            ENGINE, "trend", "trend_episode_duration",
            f"Directional-change episodes (threshold {thr:.4f} log) vs 200 shuffled-return paths (TRAIN)",
            "{} to {}".format(*self.splits.span("train")), episodes=int(len(obs)),
            mean_duration=float(obs.mean()) if len(obs) else None,
            median_duration=float(np.median(obs)) if len(obs) else None,
            shuffled_mean_duration=float(np.mean(sims)), p_longer_than_shuffled=float(p))

    def regime_findings(self) -> list[Finding]:
        out: list[Finding] = []
        try:
            self.regimes = fit_regimes(self.ds.bars["close"], self.splits.slice("train"), seed=self.seed)
        except Exception as exc:  # insufficient data or numerical failure: report, do not crash
            return [Finding.insufficient(ENGINE, "regimes", "regime_discovery", str(exc))]
        rm = self.regimes
        reg = rm.predict(self.ds.bars["close"])
        out.append(Finding.descriptive(ENGINE, "regimes", "regime_model",
                                       f"GMM regimes on TRAIN, k={rm.k} chosen by BIC", "{} to {}".format(*self.splits.span("train")),
                                       labels=rm.labels, bic=rm.bic, centroids=rm.centroids.round(4).to_dict("index"),
                                       **rm.stats))
        self._regime_series = reg
        return out

    def regime_tests(self) -> list[BehaviorTest]:
        if self.regimes is None:
            return []
        T = []
        reg = self._regime_series
        for k, label in self.regimes.labels.items():
            for h in [5, 20]:
                T.append(BehaviorTest("regimes", f"regime{k}_fwd{h}", f"next {h}-bar return in {label} (vs other regimes)",
                                      self._cond_test(self.fwd[h], reg == k, lags=h)))
        return T

    # ---- run -----------------------------------------------------------------------------------
    def run(self, fdr_alpha: float = 0.05) -> list[Finding]:
        findings: list[Finding] = []
        findings += self.descriptive()
        findings += self.regime_findings()
        tests = self.build_tests() + self.regime_tests()
        span = "{} to {}".format(*self.splits.span("train"))
        tested: list[Finding] = []
        fn_by_name: dict[str, Callable[[np.ndarray], TestResult]] = {}
        for t in tests:
            try:
                res = t.fn(self.train_mask)
            except Exception as exc:  # isolate failures of single tests
                log.warning("test %s failed: %s", t.name, exc)
                res = NAN_RESULT
            f = Finding.from_test(ENGINE, t.category, t.name, t.description, res, span)
            if not res.valid:
                f.status = "INSUFFICIENT DATA"
            tested.append(f)
            fn_by_name[t.name] = t.fn
        apply_fdr(tested, fdr_alpha)
        replicate(tested, lambda f: fn_by_name[f.name](self.val_mask), fdr_alpha)
        findings += tested + self.insufficiency_findings()
        n_disc = sum(f.status == "DISCOVERY" for f in findings)
        log.info("market behavior: %d tests, %d significant on train, %d replicated on validation",
                 len(tested), sum(f.significant for f in tested), n_disc)
        return findings

    def summary_table(self, findings: list[Finding]) -> list[dict[str, Any]]:
        return [f.to_dict() for f in findings]
