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
    return {k: v.astype("float64").replace([np.inf, -np.inf], np.nan).rename(k) for k, v in P.items()}


def _streak(r: pd.Series) -> pd.Series:
    s = np.sign(r.fillna(0.0)).to_numpy()
    out = np.zeros(len(s))
    for i in range(len(s)):
        if s[i] != 0 and i > 0 and np.sign(out[i - 1]) == s[i]:
            out[i] = out[i - 1] + s[i]
        else:
            out[i] = s[i]
    return pd.Series(out, index=r.index)


CATEGORICAL = {"dow", "month", "dom", "hour", "bars_into_month"}

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
    numeric = [n for n in names if n not in CATEGORICAL]
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
