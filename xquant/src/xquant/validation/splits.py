"""Chronological data splits with access control.

    TRAIN | embargo | VALIDATION | embargo | TEST | embargo | FINAL (out-of-sample)

* TRAIN: free use (feature discovery, hypothesis tests, evolution fitness).
* VALIDATION: gate only. Candidates are *evaluated* there, never fitted. Each evaluation is logged.
* TEST: evaluated once per finalist after all selection is frozen. Re-optimising after seeing TEST is
  forbidden: ``SplitGuard`` refuses optimisation requests once TEST has been opened.
* FINAL: opened once, for the single top-ranked strategy, at the very end of a research cycle.

The guard is persisted in the research memory so the rule survives across runs.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

from xquant.config import SplitSpec
from xquant.errors import InsufficientDataError, SplitAccessError

SplitName = Literal["train", "validation", "test", "final"]
SPLITS: tuple[SplitName, ...] = ("train", "validation", "test", "final")


@dataclass
class DataSplits:
    index: pd.DatetimeIndex
    bounds: dict[str, tuple[int, int]]  # name -> [start, end) positional

    def slice(self, name: SplitName) -> builtins.slice:
        a, b = self.bounds[name]
        return builtins.slice(a, b)

    def mask(self, name: SplitName) -> pd.Series:
        m = pd.Series(False, index=self.index)
        a, b = self.bounds[name]
        m.iloc[a:b] = True
        return m

    def span(self, name: SplitName) -> tuple[str, str]:
        a, b = self.bounds[name]
        if b <= a:
            return ("", "")
        return (str(self.index[a].date()), str(self.index[b - 1].date()))

    def sizes(self) -> dict[str, int]:
        return {k: b - a for k, (a, b) in self.bounds.items()}

    def upto(self, name: SplitName) -> builtins.slice:
        """Positions from the start of data to the end of ``name`` (used for walk-forward re-fits)."""
        return builtins.slice(0, self.bounds[name][1])


def make_splits(index: pd.DatetimeIndex, spec: SplitSpec, min_size: int = 100) -> DataSplits:
    def pos_after(d: object) -> int:
        ts = pd.Timestamp(str(d)).tz_localize("UTC") + pd.Timedelta(days=1)
        return int(index.searchsorted(ts, side="left"))

    e = spec.embargo_bars
    n = len(index)
    t_end, v_end, s_end = pos_after(spec.train_end), pos_after(spec.validation_end), pos_after(spec.test_end)
    bounds = {"train": (0, t_end), "validation": (min(t_end + e, n), v_end),
              "test": (min(v_end + e, n), s_end), "final": (min(s_end + e, n), n)}
    sizes = {k: b - a for k, (a, b) in bounds.items()}
    small = {k: v for k, v in sizes.items() if v < min_size}
    if small:
        raise InsufficientDataError(f"splits too small {small} (min {min_size}); adjust split dates")
    return DataSplits(index=index, bounds=bounds)


@dataclass
class SplitGuard:
    """Tracks protected-split usage. ``log`` entries are persisted by the experiment tracker."""

    test_opened: bool = False
    final_opened: bool = False
    validation_evaluations: int = 0
    log: list[dict[str, str]] = field(default_factory=list)

    def request(self, split: SplitName, purpose: Literal["optimize", "evaluate"], who: str) -> None:
        if purpose == "optimize" and split != "train":
            raise SplitAccessError(f"{who}: optimisation is only allowed on TRAIN (requested {split})")
        if purpose == "optimize" and self.test_opened:
            raise SplitAccessError(f"{who}: TEST already opened in this research cycle - optimisation is frozen")
        if split == "validation":
            self.validation_evaluations += 1
        if split == "final" and self.final_opened:
            raise SplitAccessError(f"{who}: FINAL out-of-sample may be opened only once per research cycle")
        if split == "test":
            self.test_opened = True
        if split == "final":
            self.final_opened = True
        self.log.append({"split": split, "purpose": purpose, "who": who,
                         "at": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds")})
