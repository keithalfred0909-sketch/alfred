"""Feature primitives and the expression grammar used for feature discovery.

Every primitive is a *causal* transformation: its value at bar t depends only on bars <= t (and on
exogenous series already point-in-time aligned). ``assert_causal`` verifies this empirically by
truncation: the value at t computed on data[:t+1] must equal the value computed on the full data.

Expressions compose primitives with a small set of operators; complexity = number of nodes. Primitives
are generic mathematical transforms of price, time and exogenous data - not named trading indicators.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from xquant.errors import LookAheadError

# ---------------------------------------------------------------------------------------------------
# primitives


def _roll_rank(s: pd.Series, w: int) -> pd.Series:
    """Percentile of the current value within the trailing window (causal)."""
    return s.rolling(w, min_periods=max(5, int(w * 0.75))).rank(pct=True)


def build_primitives(bars: pd.DataFrame, exog: pd.DataFrame | None, tz: str = "UTC") -> dict[str, pd.Series]:
    c = bars["close"]
    lc = np.log(c)
    r = lc.diff()
    P: dict[str, pd.Series] = {}
    for k in [1, 2, 3, 5, 10, 20, 60, 120]:
        P[f"ret_{k}"] = lc - lc.shift(k)
    vol: dict[int, pd.Series] = {}
    for w in [5, 10, 20, 60, 120]:
        vol[w] = r.rolling(w, min_periods=max(4, int(w * 0.75))).std()
        P[f"vol_{w}"] = np.log(vol[w])
    for a, b in [(5, 60), (10, 120), (20, 120), (5, 20)]:
        P[f"volratio_{a}_{b}"] = np.log(vol[a] / vol[b])  # type: ignore[assignment]
    for w in [10, 20, 60, 120, 250]:
        m = lc.rolling(w, min_periods=int(w * 0.75)).mean()
        sd = r.rolling(w, min_periods=int(w * 0.75)).std() * math.sqrt(w)
        P[f"zdist_{w}"] = (lc - m) / sd
    for w in [20, 60, 250]:
        P[f"fromhigh_{w}"] = (lc - lc.rolling(w, min_periods=int(w * 0.75)).max()) / vol[20]
        P[f"fromlow_{w}"] = (lc - lc.rolling(w, min_periods=int(w * 0.75)).min()) / vol[20]
    for w in [10, 20, 60]:
        P[f"efficiency_{w}"] = (lc - lc.shift(w)).abs() / r.abs().rolling(w, min_periods=int(w * 0.75)).sum()
    for w in [20, 60]:
        P[f"skew_{w}"] = r.rolling(w, min_periods=int(w * 0.75)).skew()
    P["autocorr_60"] = r.rolling(60, min_periods=45).corr(r.shift(1))
    P["shock_1"] = r / vol[60].shift(1)
    P["streak"] = _streak(r)
    local = pd.DatetimeIndex(bars.index).tz_convert(tz)
    P["dow"] = pd.Series(local.dayofweek.astype(float), index=bars.index)
    P["month"] = pd.Series(local.month.astype(float), index=bars.index)
    P["dom"] = pd.Series(local.day.astype(float), index=bars.index)
    mid = pd.Series(local.year * 12 + local.month, index=bars.index)
    P["bars_into_month"] = mid.groupby(mid).cumcount().astype(float)
    if local.hour.nunique() > 1:
        P["hour"] = pd.Series(local.hour.astype(float), index=bars.index)
        P.update(session_features(bars, local, vol[20]))
        if len(bars) > 2 and pd.to_timedelta(pd.Series(bars.index).diff().median()) <= pd.Timedelta("30min"):
            P.update(intraday_momentum_features(c, local))
    if bars[["open", "high", "low"]].notna().all(axis=None):
        rng_ = np.log(bars["high"] / bars["low"])
        P["range_vol"] = rng_ / vol[20]
        P["close_loc"] = (bars["close"] - bars["low"]) / (bars["high"] - bars["low"]).replace(0, np.nan)
        P["gap"] = np.log(bars["open"] / c.shift(1)) / vol[20]
    if bars["volume"].notna().any():
        lv = np.log(bars["volume"].replace(0, np.nan))
        P["volume_z"] = (lv - lv.rolling(60, min_periods=45).mean()) / lv.rolling(60, min_periods=45).std()
    if exog is not None:
        for col in exog.columns:
            x = exog[col].astype(float)
            P[f"x_{col}"] = x
            for k in [5, 20, 63]:
                P[f"x_{col}_chg{k}"] = x - x.shift(k)
            P[f"x_{col}_z250"] = (x - x.rolling(250, min_periods=180).mean()) / x.rolling(250, min_periods=180).std()
            if col.startswith("px_") and (x.dropna() > 0).all() and x.notna().sum() > 300:
                # relative value (price series named px_*): z-score of the log spread vs the other asset
                spread = lc - np.log(x)
                for w in (60, 250):
                    P[f"x_{col}_relz{w}"] = (spread - spread.rolling(w, min_periods=int(w * 0.75)).mean()) / \
                        spread.rolling(w, min_periods=int(w * 0.75)).std()
                P.update(divergence_features(lc, pd.Series(np.log(x), index=x.index), col))
    return {k: v.astype("float64").replace([np.inf, -np.inf], np.nan).rename(k) for k, v in P.items()}


def divergence_features(la: pd.Series, lx: pd.Series, col: str, beta_window: int = 500) -> dict[str, pd.Series]:
    """Divergence between the asset (log price ``la``) and a related price series (log ``lx``).

    * ``x_{col}_div{k}``: k-bar asset return minus beta * the other series' k-bar return, z-scored. Beta is
      the trailing regression slope of 1-bar returns (negative for an inverse pair such as EURUSD vs DXY),
      so the residual is the part of the asset's move the other series did NOT explain.
    * ``x_{col}_smt{w}`` (categorical): "SMT" divergence on closes. +1 when the asset closes below its
      previous w-bar low but the other series does not confirm (no new low if it moves with the asset, no
      new high if it moves inversely); -1 for the mirror case at highs; 0 otherwise. The direction of the
      relationship is the sign of the trailing beta at that bar. Everything uses data up to the bar close.
    """
    ra, rx = la.diff(), lx.diff()
    minp = int(beta_window * 0.75)
    beta = ra.rolling(beta_window, min_periods=minp).cov(rx) / rx.rolling(beta_window, min_periods=minp).var()
    out: dict[str, pd.Series] = {}
    for k in (1, 5, 20):
        resid = (la - la.shift(k)) - beta * (lx - lx.shift(k))
        out[f"x_{col}_div{k}"] = resid / resid.rolling(250, min_periods=180).std()
    inverse = beta < 0
    for w in (20, 60):
        a_lo = la < la.shift(1).rolling(w, min_periods=w).min()
        a_hi = la > la.shift(1).rolling(w, min_periods=w).max()
        x_lo = lx < lx.shift(1).rolling(w, min_periods=w).min()
        x_hi = lx > lx.shift(1).rolling(w, min_periods=w).max()
        confirm_low = np.where(inverse, x_hi, x_lo)
        confirm_high = np.where(inverse, x_lo, x_hi)
        smt = np.where(a_lo & ~confirm_low, 1.0, np.where(a_hi & ~confirm_high, -1.0, 0.0))
        valid = beta.notna() & lx.shift(w).notna() & la.shift(w).notna()
        out[f"x_{col}_smt{w}"] = pd.Series(np.where(valid, smt, np.nan), index=la.index)
    return out


def session_features(bars: pd.DataFrame, local: pd.DatetimeIndex, vol: pd.Series,
                     roll: str = "17:00", ny_anchor_h: float = 16.0) -> dict[str, pd.Series]:
    """Causal session-structure features for intraday bars (bars stamped at their close).

    The trading day rolls at ``roll`` local time (17:00 New York, the FX/futures convention). The first
    ``ny_anchor_h`` hours of a session (17:00 -> 09:00 NY) form the overnight range. Every value at bar t
    uses only bars of the current session up to t and completed previous sessions.
    """
    c = bars["close"]
    hi = bars["high"].fillna(c)
    lo = bars["low"].fillna(c)
    op = bars["open"].fillna(c.shift(1))
    naive = local.tz_localize(None)
    rd = pd.Timedelta(roll + ":00")
    day = (naive - rd - pd.Timedelta(seconds=1)).floor("D")
    key = pd.Series(day, index=bars.index)
    hours_in = pd.Series(((naive - rd - day) / pd.Timedelta(hours=1)).to_numpy(), index=bars.index)
    g = lambda s: s.groupby(key.to_numpy())  # noqa: E731
    sess_open = g(op).transform("first")
    run_hi, run_lo = g(hi).cummax(), g(lo).cummin()
    v = vol.replace(0, np.nan)
    out: dict[str, pd.Series] = {}
    out["sess_ret"] = np.log(c / sess_open) / v
    out["sess_pos"] = (c - run_lo) / (run_hi - run_lo).replace(0, np.nan)
    out["sess_bar"] = g(c).cumcount().astype(float)
    daily = pd.DataFrame({"h": g(hi).max(), "l": g(lo).min()}).shift(1)  # previous COMPLETED session
    ph = key.map(daily["h"]).astype(float)
    pl = key.map(daily["l"]).astype(float)
    out["pday_pos"] = (c - pl) / (ph - pl).replace(0, np.nan)
    out["pday_hi"] = np.log(c / ph) / v
    out["pday_lo"] = np.log(c / pl) / v
    on = hours_in <= ny_anchor_h  # overnight part of the session (bar closes up to 09:00 NY)
    on_hi = g(hi.where(on)).cummax()
    on_lo = g(lo.where(on)).cummin()
    anchor = g(c.where(on)).ffill()
    on_hi, on_lo = g(on_hi).ffill(), g(on_lo).ffill()
    after = ~on
    out["on_pos"] = ((c - on_lo) / (on_hi - on_lo).replace(0, np.nan)).where(after)
    out["ny_ret"] = (np.log(c / anchor) / v).where(after)
    return {k: s.astype("float64").replace([np.inf, -np.inf], np.nan).rename(k) for k, s in out.items()}


def intraday_momentum_features(close: pd.Series, local: pd.DatetimeIndex, open_hm: int = 600,
                               close_hm: int = 960, max_gap_days: int = 4) -> dict[str, pd.Series]:
    """US cash-session structure for sub-hourly bars stamped at their close (New York time).

    * ``tod`` (categorical): minutes after local midnight of the bar close (15:30 -> 930).
    * ``im_open_ret``: log return from the previous trading day's 16:00 close to today's 10:00 close (the
      "first half-hour" return of Gao, Han, Li & Zhou 2018, overnight included); defined on today's bars
      from 10:00 to 16:00, NaN elsewhere. ``im_open_sign`` (categorical) is its sign.
    Only closes already printed are used; a previous close older than ``max_gap_days`` is not used.
    """
    naive = local.tz_localize(None)
    mins = np.asarray(naive.hour * 60 + naive.minute)
    date = pd.DatetimeIndex(naive.normalize())
    lc = np.log(close.to_numpy(dtype=float))
    out: dict[str, pd.Series] = {"tod": pd.Series(mins.astype(float), index=close.index)}
    closes = pd.Series(lc[mins == close_hm], index=date[mins == close_hm])
    closes = closes[~closes.index.duplicated(keep="last")]
    opens = pd.Series(lc[mins == open_hm], index=date[mins == open_hm])
    opens = opens[~opens.index.duplicated(keep="last")]
    first = pd.Series(np.nan, index=opens.index)
    if len(closes) and len(opens):
        pos = np.searchsorted(closes.index.to_numpy(), opens.index.to_numpy(), side="left") - 1  # strictly earlier day
        ok = pos >= 0
        prev_val = np.where(ok, closes.to_numpy()[np.clip(pos, 0, None)], np.nan)
        prev_day = np.where(ok, closes.index.to_numpy()[np.clip(pos, 0, None)], np.datetime64("NaT"))
        fresh = ok & ((opens.index.to_numpy() - prev_day) <= np.timedelta64(max_gap_days, "D"))
        first = pd.Series(np.where(fresh, opens.to_numpy() - prev_val, np.nan), index=opens.index)
    in_day = (mins >= open_hm) & (mins <= close_hm)
    val = pd.Series(date, index=close.index).map(first).to_numpy(dtype=float)
    ret = pd.Series(np.where(in_day, val, np.nan), index=close.index)
    out["im_open_ret"] = ret
    out["im_open_sign"] = pd.Series(np.sign(ret.to_numpy()), index=close.index)
    return out


def _streak(r: pd.Series) -> pd.Series:
    s = np.sign(r.fillna(0.0)).to_numpy()
    out = np.zeros(len(s))
    for i in range(len(s)):
        if s[i] != 0 and i > 0 and np.sign(out[i - 1]) == s[i]:
            out[i] = out[i - 1] + s[i]
        else:
            out[i] = s[i]
    return pd.Series(out, index=r.index)


CATEGORICAL = {"dow", "month", "dom", "hour", "bars_into_month", "sess_bar", "tod", "im_open_sign"}
_CATEGORICAL_PATTERN = re.compile(r"_smt\d+$")


def is_categorical(name: str) -> bool:
    """Discrete-valued primitive: handled by bucket (==) conditions, never by quantile tails."""
    return name in CATEGORICAL or bool(_CATEGORICAL_PATTERN.search(name))

# ---------------------------------------------------------------------------------------------------
# expression grammar


@dataclass(frozen=True)
class Expr:
    op: str  # "prim" | unary op | binary op
    args: tuple[Expr, ...] = ()
    name: str = ""  # primitive name
    param: int = 0

    def key(self) -> str:
        if self.op == "prim":
            return self.name
        inner = ",".join(a.key() for a in self.args)
        return f"{self.op}({inner}{',' + str(self.param) if self.param else ''})"

    @property
    def complexity(self) -> int:
        return 1 + sum(a.complexity for a in self.args)

    def primitives(self) -> set[str]:
        if self.op == "prim":
            return {self.name}
        return set().union(*(a.primitives() for a in self.args))


UNARY: dict[str, Callable[[pd.Series, int], pd.Series]] = {
    "zscore": lambda s, w: (s - s.rolling(w, min_periods=int(w * 0.75)).mean()) / s.rolling(w, min_periods=int(w * 0.75)).std(),
    "rank": lambda s, w: _roll_rank(s, w),
    "diff": lambda s, k: s - s.shift(k),
    "smooth": lambda s, w: s.rolling(w, min_periods=max(2, int(w * 0.75))).mean(),
    "abs": lambda s, _: s.abs(),
}
UNARY_PARAMS = {"zscore": [20, 60, 250], "rank": [60, 250], "diff": [1, 5, 20], "smooth": [3, 5, 10], "abs": [0]}
BINARY: dict[str, Callable[[pd.Series, pd.Series], pd.Series]] = {
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
}


def evaluate(expr: Expr, prims: dict[str, pd.Series], cache: dict[str, pd.Series] | None = None) -> pd.Series:
    cache = {} if cache is None else cache
    k = expr.key()
    if k in cache:
        return cache[k]
    if expr.op == "prim":
        out = prims[expr.name]
    elif expr.op in UNARY:
        out = UNARY[expr.op](evaluate(expr.args[0], prims, cache), expr.param)
    elif expr.op in BINARY:
        a, b = (evaluate(x, prims, cache) for x in expr.args)
        out = BINARY[expr.op](_std(a), _std(b))
    else:
        raise ValueError(f"unknown op {expr.op}")
    out = out.replace([np.inf, -np.inf], np.nan).rename(k)
    cache[k] = out
    return out


def _std(s: pd.Series) -> pd.Series:
    """Causal scale normalisation so binary ops combine comparable magnitudes."""
    return s / s.abs().expanding(min_periods=60).mean()


def prim(name: str) -> Expr:
    return Expr("prim", name=name)


def random_expr(rng: np.random.Generator, names: list[str], max_complexity: int) -> Expr:
    numeric = [n for n in names if not is_categorical(n)]
    e = prim(str(rng.choice(numeric)))
    while e.complexity < max_complexity and rng.random() < 0.7:
        if rng.random() < 0.7 or e.complexity + 2 > max_complexity:
            op = str(rng.choice(list(UNARY)))
            if op == "abs" and e.op == "abs":
                continue
            e = Expr(op, (e,), param=int(rng.choice(UNARY_PARAMS[op])))
        else:
            op = str(rng.choice(list(BINARY)))
            other = prim(str(rng.choice(numeric)))
            if other.key() == e.key():
                continue
            e = Expr(op, tuple(sorted([e, other], key=lambda x: x.key())))
    return e


def parse_key(key: str) -> Expr:
    """Inverse of Expr.key() (used when reloading genomes from memory)."""
    key = key.strip()
    if "(" not in key:
        return prim(key)
    op, rest = key.split("(", 1)
    body = rest[:-1]
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
            continue
        depth += ch == "("
        depth -= ch == ")"
        cur += ch
    parts.append(cur)
    if op in BINARY:
        return Expr(op, (parse_key(parts[0]), parse_key(parts[1])))
    param = int(parts[1]) if len(parts) > 1 else 0
    return Expr(op, (parse_key(parts[0]),), param=param)


def expr_hash(key: str) -> str:
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def assert_causal(compute: Callable[[pd.DataFrame], pd.Series], bars: pd.DataFrame, cut_points: list[int],
                  name: str = "feature", atol: float = 1e-9) -> None:
    """Truncation test: value at bar t must not change when data after t is removed."""
    full = compute(bars)
    for t in cut_points:
        part = compute(bars.iloc[: t + 1])
        a, b = full.iloc[t], part.iloc[-1]
        if (pd.isna(a) != pd.isna(b)) or (not pd.isna(a) and abs(a - b) > atol * max(1.0, abs(a))):
            raise LookAheadError(f"{name}: value at {bars.index[t]} changes with future data ({a} vs {b})")
