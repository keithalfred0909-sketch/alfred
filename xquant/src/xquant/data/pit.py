"""Point-in-time alignment of exogenous series (macro, cross-asset) onto the bar clock.

Each observation gets an ``available_at`` timestamp = end of its reference period + availability lag.
A bar at time t may only see observations with ``available_at <= t``. This is the single choke point
through which exogenous information enters the lab, so look-ahead through macro data is structurally
impossible as long as lags are configured conservatively.

Known limitation: the redistributed macro files carry latest-vintage (revised) values, not first
releases. CPI-U NSA is essentially unrevised; other series may carry mild revision look-ahead. This is
recorded in the dataset notes and in every report.
"""

from __future__ import annotations

import pandas as pd

from xquant.errors import LookAheadError


def period_end(ts: pd.DatetimeIndex, frequency: str) -> pd.DatetimeIndex:
    naive = ts.tz_convert(None) if ts.tz is not None else ts
    if frequency == "monthly":
        end = naive.to_period("M").to_timestamp(how="end")
    elif frequency == "quarterly":
        end = naive.to_period("Q").to_timestamp(how="end")
    elif frequency == "daily":
        end = naive.normalize() + pd.Timedelta("23:59:59")
    elif frequency == "bar":
        end = naive  # already stamped at the moment the value is known (bar close)
    else:
        raise ValueError(f"unknown frequency {frequency}")
    return pd.DatetimeIndex(end).floor("s")


def transform_series(s: pd.Series, transform: str, frequency: str) -> pd.Series:
    if transform == "level":
        return s
    periods = {"monthly": 12, "quarterly": 4, "daily": 252, "bar": 252}[frequency]
    if transform == "yoy":
        return 100.0 * (s / s.shift(periods) - 1.0)
    if transform == "diff":
        return s.diff()
    raise ValueError(f"unknown transform {transform}")


def align_point_in_time(series: pd.Series, bar_index: pd.DatetimeIndex, frequency: str, lag_days: int,
                        tz: str = "UTC") -> pd.Series:
    """Return ``series`` sampled on ``bar_index`` using only values already available at each bar.

    ``series`` is indexed by reference-period stamps (naive dates in ``tz`` or tz-aware).
    """
    s = series.dropna().sort_index()
    if s.empty:
        return pd.Series(index=bar_index, dtype="float64", name=series.name)
    stamps = pd.DatetimeIndex(s.index)
    end = period_end(stamps, frequency)
    avail = (end + pd.Timedelta(days=lag_days)).tz_localize(tz, ambiguous="NaT", nonexistent="shift_forward")
    avail = avail.tz_convert("UTC")
    src = pd.DataFrame({"available_at": avail, "value": s.to_numpy()}).dropna().sort_values("available_at")
    tgt = pd.DataFrame({"t": bar_index})
    merged = pd.merge_asof(tgt, src, left_on="t", right_on="available_at", direction="backward")
    if (merged["available_at"] > merged["t"]).any():  # defensive: merge_asof contract
        raise LookAheadError("point-in-time alignment produced a future observation")
    return pd.Series(merged["value"].to_numpy(), index=bar_index, name=series.name)
