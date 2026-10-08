"""EXPECTATION ENGINE: separates expectation, reality, surprise and market reaction.

    expectation = consensus (survey) published before the release
    reality     = actual
    surprise    = actual - consensus                (NaN when consensus is unknown: never imputed)
    std_surprise= surprise / std(past surprises of the same event)   (point-in-time, expanding)
    change      = actual - previous                 (NOT a surprise; kept separately and labelled)

The standardisation uses only surprises released strictly before each event, so a z-score never
contains information from later releases.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MIN_HISTORY = 8  # past surprises required before a standardised surprise is defined


def compute_surprises(events: pd.DataFrame) -> pd.DataFrame:
    """Add surprise columns to a calendar frame (UTC index; columns event, previous, consensus, actual)."""
    ev = events.sort_index().copy()
    ev["surprise"] = ev["actual"] - ev["consensus"]
    ev["change_vs_previous"] = ev["actual"] - ev["previous"]
    ev["std_surprise"] = np.nan
    for _, g in ev.groupby("event", sort=False):
        s = g["surprise"]
        past_std = s.expanding(min_periods=MIN_HISTORY).std().shift(1)
        ev.loc[g.index, "std_surprise"] = (s / past_std).to_numpy()
    ev["surprise_sign"] = np.sign(ev["surprise"])
    ev["magnitude"] = pd.cut(ev["std_surprise"].abs(), [0, 0.5, 1.5, np.inf], labels=["small", "medium", "large"],
                             include_lowest=True)
    ev["has_expectation"] = ev["consensus"].notna()
    return ev


def expectation_coverage(events: pd.DataFrame) -> pd.DataFrame:
    """Per event type: how many releases have consensus and a defined standardised surprise."""
    ev = compute_surprises(events)
    return ev.groupby("event").agg(releases=("actual", "size"), with_consensus=("has_expectation", "sum"),
                                   with_std_surprise=("std_surprise", lambda x: int(x.notna().sum())))
