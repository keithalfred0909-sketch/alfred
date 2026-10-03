"""Normalisation and cleaning with a full audit trail.

Policy: remove what is provably wrong, flag what is suspicious, never fill. Missing bars stay missing;
the research engines handle gaps explicitly. Every action is counted in the ``QualityReport``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from xquant.data.schema import BAR_COLUMNS, bar_timedelta
from xquant.errors import DataQualityError


@dataclass
class QualityReport:
    rows_in: int = 0
    rows_out: int = 0
    unparseable_timestamps: int = 0
    exact_duplicates: int = 0
    conflicting_duplicates: int = 0
    missing_close: int = 0
    non_positive: int = 0
    ohlc_inconsistent: int = 0
    spikes_removed: int = 0
    spike_timestamps: list[str] = field(default_factory=list)
    gaps: int = 0
    largest_gap: str = ""
    extreme_moves_kept: int = 0
    notes: list[str] = field(default_factory=list)
    verdict: str = "OK"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def localize_index(idx: pd.DatetimeIndex, tz: str, close_time: str | None) -> pd.DatetimeIndex:
    """Make an index tz-aware UTC. Date-only stamps get ``close_time`` (local) as the decision time;
    without one, the conservative end of day (23:59:59 local) is used."""
    if idx.tz is None:
        is_date_only = bool((idx.dropna() == idx.dropna().normalize()).all())
        if is_date_only:
            t = pd.Timedelta(close_time + ":00") if close_time else pd.Timedelta("23:59:59")
            idx = idx + t
        idx = idx.tz_localize(tz, ambiguous="NaT", nonexistent="NaT")
    return idx.tz_convert("UTC").rename("timestamp")


def clean_bars(raw: pd.DataFrame, tz: str, timeframe: str, close_time: str | None = None,
               spike_sigma: float = 8.0) -> tuple[pd.DataFrame, QualityReport]:
    rep = QualityReport(rows_in=len(raw))
    df = raw.copy()
    if "value" in df.columns and "close" not in df.columns:
        df = df.rename(columns={"value": "close"})
    if "close" not in df.columns:
        raise DataQualityError("price source has no close/value column")
    for c in BAR_COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    extra = [c for c in df.columns if c not in BAR_COLUMNS and c == "spread"]
    df = df[BAR_COLUMNS + extra].astype("float64")

    idx = localize_index(pd.DatetimeIndex(df.index), tz, close_time)
    df.index = idx
    bad_ts = df.index.isna()
    rep.unparseable_timestamps = int(bad_ts.sum())
    df = df[~bad_ts].sort_index(kind="stable")

    # Duplicates: identical rows are harmless; conflicting values for one timestamp are a data error.
    dup_full = df.reset_index().duplicated(keep="first").to_numpy()
    rep.exact_duplicates = int(dup_full.sum())
    df = df[~dup_full]
    dup_ts = df.index.duplicated(keep="last")
    rep.conflicting_duplicates = int(dup_ts.sum())
    df = df[~dup_ts]

    miss = df["close"].isna()
    rep.missing_close = int(miss.sum())
    df = df[~miss]

    nonpos = (df[["open", "high", "low", "close"]] <= 0).any(axis=1)
    rep.non_positive = int(nonpos.sum())
    df = df[~nonpos]

    has_ohlc = df[["open", "high", "low"]].notna().all(axis=1)
    hi_bad = df["high"] < df[["open", "close", "low"]].max(axis=1) - 1e-12
    lo_bad = df["low"] > df[["open", "close", "high"]].min(axis=1) + 1e-12
    incons = has_ohlc & (hi_bad | lo_bad)
    rep.ohlc_inconsistent = int(incons.sum())
    df = df[~incons]

    df, rep = _remove_spikes(df, rep, spike_sigma)
    _gap_report(df, timeframe, rep)

    rep.rows_out = len(df)
    corrupt = rep.non_positive + rep.ohlc_inconsistent + rep.conflicting_duplicates + rep.unparseable_timestamps
    if rep.rows_out < 250:
        rep.verdict = "FAIL"
        rep.notes.append(f"only {rep.rows_out} usable bars")
    elif corrupt > 0.05 * max(rep.rows_in, 1):
        rep.verdict = "FAIL"
        rep.notes.append(f"{corrupt} corrupt rows (>5%)")
    elif corrupt or rep.spikes_removed:
        rep.verdict = "WARN"
    return df, rep


def _remove_spikes(df: pd.DataFrame, rep: QualityReport, k: float) -> tuple[pd.DataFrame, QualityReport]:
    """Remove isolated bad prints: a jump of > k robust sigmas that is fully reversed on the next bar
    (price returns to within 1 robust sigma of the previous close). Genuine large moves that do not
    revert are kept and only counted."""
    r = np.log(df["close"]).diff()
    mad = (r - r.rolling(250, min_periods=50).median()).abs().rolling(250, min_periods=50).median()
    sigma = (1.4826 * mad).shift(1)
    big = r.abs() > k * sigma
    rep.extreme_moves_kept = int(big.sum())
    nxt = r.shift(-1)
    prev_close = df["close"].shift(1)
    after = df["close"].shift(-1)
    back = (np.log(after / prev_close)).abs() < sigma
    spike = big & (np.sign(nxt) == -np.sign(r)) & (nxt.abs() > 0.8 * r.abs()) & back
    if spike.any():
        rep.spikes_removed = int(spike.sum())
        rep.extreme_moves_kept -= rep.spikes_removed
        rep.spike_timestamps = [str(t) for t in df.index[spike.fillna(False).to_numpy()]][:50]
        df = df[~spike.fillna(False).to_numpy()]
    return df, rep


def _gap_report(df: pd.DataFrame, timeframe: str, rep: QualityReport) -> None:
    if len(df) < 2:
        return
    step = bar_timedelta(timeframe)
    deltas = df.index.to_series().diff().dropna()
    if step >= pd.Timedelta("1D"):
        # Daily data: weekends and single holidays are normal; count gaps longer than 4 calendar days.
        gaps = deltas[deltas > pd.Timedelta("4D")]
    else:
        gaps = deltas[(deltas > 3 * step) & (deltas < pd.Timedelta("2D"))]  # ignore weekend closures
    rep.gaps = int(len(gaps))
    if len(gaps):
        t = gaps.idxmax()
        rep.largest_gap = f"{gaps.max()} ending {t}"
