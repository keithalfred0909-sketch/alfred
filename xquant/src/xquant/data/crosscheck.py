"""Cross-source validation: compare an intraday price source with an independent daily reference.

For EUR/USD the reference is the Federal Reserve H.10 noon buying rate in New York. For every reference
date, the intraday bar that CLOSES at the reference local time (12:00 New York) is matched and compared:

* level agreement: median and 95th percentile absolute difference in bps
* return agreement: correlation of day-over-day changes

A timezone error (bars shifted by hours), a wrong price scale, inverted quotes or a misread file format
all break at least one of these, so the check turns silent corruption into a loud failure.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from xquant.errors import DataQualityError


def cross_check_daily(bars: pd.DataFrame, reference: pd.Series, local_time: str = "12:00",
                      tz: str = "America/New_York", max_median_bps: float = 10.0,
                      min_return_corr: float = 0.9, min_matches: int = 100) -> dict[str, Any]:
    """``bars``: UTC-indexed intraday bars (stamped at close). ``reference``: UTC-indexed daily values
    stamped at their observation time (as produced by the data engine)."""
    ref_local = pd.DatetimeIndex(reference.index).tz_convert(tz)
    target = (ref_local.normalize() + pd.Timedelta(local_time + ":00")).tz_convert("UTC")
    pos = bars.index.searchsorted(target, side="left")
    ok = pos < len(bars)
    pos_ok = pos[ok]
    matched_t = bars.index[pos_ok]
    exact = np.asarray(matched_t == target[ok])
    px = bars["close"].to_numpy()[pos_ok][exact]
    ref = reference.to_numpy()[ok][exact]
    n = int(len(px))
    if n < min_matches:
        raise DataQualityError(f"cross-check: only {n} reference dates have a bar closing exactly at {local_time} {tz}")
    diff_bps = np.abs(px / ref - 1) * 1e4
    rp, rr = np.diff(np.log(px)), np.diff(np.log(ref))
    corr = float(np.corrcoef(rp, rr)[0, 1]) if n > 2 else float("nan")
    out: dict[str, Any] = {"matches": n, "median_abs_diff_bps": float(np.median(diff_bps)),
           "p95_abs_diff_bps": float(np.quantile(diff_bps, 0.95)), "return_corr": corr,
           "local_time": local_time, "tz": tz}
    # The same check one hour off: if a shifted clock fits better, the source's timestamps are wrong.
    for shift in (-1, 1):
        t2 = target + pd.Timedelta(hours=shift)
        p2 = bars.index.searchsorted(t2, side="left")
        m2 = (p2 < len(bars))
        hit = np.zeros(len(t2), dtype=bool)
        hit[m2] = bars.index[p2[m2]] == t2[m2]
        if hit.sum() >= min_matches:
            a = bars["close"].to_numpy()[p2[hit]]
            b = reference.to_numpy()[hit]
            out[f"median_abs_diff_bps_shift{shift:+d}h"] = float(np.median(np.abs(a / b - 1) * 1e4))
    med = float(out["median_abs_diff_bps"])
    if med > max_median_bps or not corr >= min_return_corr:
        raise DataQualityError(f"cross-check FAILED vs reference: {out}")
    better = [k for k in out if k.startswith("median_abs_diff_bps_shift") and float(out[k]) < 0.7 * med]
    if better:
        raise DataQualityError(f"cross-check: a shifted clock matches the reference better ({better}) - "
                               f"timestamps are probably off by an hour: {out}")
    closer = [k for k in out if k.startswith("median_abs_diff_bps_shift") and float(out[k]) < med]
    if closer:  # not conclusive (the fixing itself is noisy) but worth flagging in every report
        out["warning"] = f"a +/-1h shifted clock matches marginally better ({closer}); verify the source timezone"
    out["status"] = "PASSED"
    return out
