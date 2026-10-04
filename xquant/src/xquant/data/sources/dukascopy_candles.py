"""Dukascopy historical candles (BID and ASK), the efficient way to get years of intraday FX/metals data.

Public datafeed layout (months are ZERO-based, timestamps UTC):

    {base}/{INSTR}/{YYYY}/BID_candles_day_1.bi5                     one file per year, daily candles
    {base}/{INSTR}/{YYYY}/{MM}/BID_candles_hour_1.bi5               one file per month, hourly candles
    {base}/{INSTR}/{YYYY}/{MM}/{DD}/BID_candles_min_1.bi5           one file per day, minute candles

Each file is LZMA-compressed; records are 24 bytes big-endian: uint32 seconds from the period start,
uint32 open, uint32 close, uint32 low, uint32 high (prices in units of ``point``), float32 volume.
Note the field order OPEN, CLOSE, LOW, HIGH. Because this layout could not be verified against the live
feed from the development container, decoding is followed by hard checks (OHLC consistency, price scale)
and the engine cross-checks the result against an independent reference (Fed noon fixing) - a wrong
interpretation fails loudly instead of producing plausible-looking garbage.

Output bars are mid prices ((bid+ask)/2) stamped at the bar CLOSE time (period start + bar length), with
the observed spread (ask-bid, mean of open and close) and Dukascopy tick volume (not exchange volume).
Flat zero-volume filler candles (market closed) are dropped and counted.
"""

from __future__ import annotations

import lzma
import threading
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from xquant.data.sources.base import CACHE_DIR, DataSource, FetchFn, register
from xquant.errors import ConfigError, DataNotFound, DataQualityError, DataUnavailableError, RateLimited
from xquant.logging_utils import get_logger

log = get_logger("data.dukascopy")

GRANULARITY = {"day": ("day_1", pd.Timedelta("1D")), "hour": ("hour_1", pd.Timedelta("1h")),
               "minute": ("min_1", pd.Timedelta("1min"))}
RECORD = np.dtype([("t", ">u4"), ("open", ">u4"), ("close", ">u4"), ("low", ">u4"), ("high", ">u4"), ("vol", ">f4")])


def decode_candles(blob: bytes, period_start: datetime, point: float) -> pd.DataFrame:
    """Decode one candle file into a frame indexed by candle OPEN time (UTC)."""
    cols = ["open", "high", "low", "close", "volume"]
    if not blob:
        return pd.DataFrame(columns=cols, dtype="float64")
    raw = lzma.decompress(blob)
    if len(raw) % RECORD.itemsize:
        raise DataQualityError(f"corrupt candle payload for {period_start}: {len(raw)} bytes")
    rec = np.frombuffer(raw, dtype=RECORD)
    base = pd.Timestamp(period_start)
    base = base.tz_localize("UTC") if base.tzinfo is None else base.tz_convert("UTC")
    idx = pd.DatetimeIndex(base + pd.to_timedelta(rec["t"].astype("int64"), unit="s"), name="timestamp")
    return pd.DataFrame({"open": rec["open"] * point, "high": rec["high"] * point, "low": rec["low"] * point,
                         "close": rec["close"] * point, "volume": rec["vol"].astype("float64")}, index=idx)


def check_candles(df: pd.DataFrame, side: str, expected_range: tuple[float, float] | None) -> None:
    """Fail loudly if decoded candles are internally inconsistent or on the wrong price scale."""
    if df.empty:
        return
    bad = (df["high"] < df[["open", "close"]].max(axis=1) - 1e-12) | (df["low"] > df[["open", "close"]].min(axis=1) + 1e-12)
    share = float(bad.mean())
    if share > 0.001:
        raise DataQualityError(f"Dukascopy {side} candles: {share:.1%} violate low<=open,close<=high - "
                               "field order or format assumption is wrong; refusing to use the data")
    if expected_range:
        med = float(df["close"].median())
        lo, hi = expected_range
        if not lo <= med <= hi:
            raise DataQualityError(f"Dukascopy {side} median price {med:.6g} outside expected {expected_range}: "
                                   "wrong `point` scaling for this instrument")


@register
class DukascopyCandleSource(DataSource):
    kind = "dukascopy_candles"
    BASE = "https://datafeed.dukascopy.com/datafeed"

    def __init__(self, instrument: str, start: str, end: str, granularity: str = "hour", point: float = 1e-5,
                 expected_range: list[float] | None = None, workers: int = 1, retries: int = 7,
                 min_interval: float = 3.0,
                 fetch: FetchFn | None = None, cache_dir: Path | None = None, **extra: Any) -> None:
        super().__init__(instrument=instrument, start=start, end=end, granularity=granularity, point=point)
        if granularity not in GRANULARITY:
            raise ConfigError(f"granularity must be one of {sorted(GRANULARITY)}")
        self.instrument, self.point, self.granularity = instrument.upper(), point, granularity
        self.start, self.end = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
        self.expected_range = (float(expected_range[0]), float(expected_range[1])) if expected_range else None
        self.workers, self.retries = workers, retries
        # Polite pacing: minimum seconds between request starts, shared by all threads. The public feed
        # throttles bursts (429/503, reset connections); pacing is faster overall than retry storms.
        self.min_interval = min_interval
        self._pace_lock = threading.Lock()
        self._next_slot = 0.0
        from xquant.data.sources.builtin import http_get
        self._fetch = fetch or http_get
        self.cache_dir = (cache_dir or CACHE_DIR) / "dukascopy_candles" / self.instrument / granularity
        self.provenance: dict[str, Any] = {}

    # ---- periods & urls ----------------------------------------------------------------------------
    def periods(self) -> Iterator[datetime]:
        cur = self.start.to_pydatetime().replace(tzinfo=UTC)
        end = self.end.to_pydatetime().replace(tzinfo=UTC)
        if self.granularity == "day":
            cur = cur.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.granularity == "hour":
            cur = cur.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            cur = cur.replace(hour=0, minute=0, second=0, microsecond=0)
        while cur < end:
            yield cur
            if self.granularity == "day":
                cur = cur.replace(year=cur.year + 1)
            elif self.granularity == "hour":
                cur = cur.replace(year=cur.year + cur.month // 12, month=cur.month % 12 + 1)
            else:
                cur = cur + pd.Timedelta("1D").to_pytimedelta()

    def url_for(self, period: datetime, side: str) -> str:
        name = f"{side}_candles_{GRANULARITY[self.granularity][0]}.bi5"
        if self.granularity == "day":
            return f"{self.BASE}/{self.instrument}/{period.year}/{name}"
        if self.granularity == "hour":
            return f"{self.BASE}/{self.instrument}/{period.year}/{period.month - 1:02d}/{name}"
        return f"{self.BASE}/{self.instrument}/{period.year}/{period.month - 1:02d}/{period.day:02d}/{name}"

    # ---- download ----------------------------------------------------------------------------------
    def _blob(self, period: datetime, side: str) -> bytes | None:
        """Cached download. Returns None when the feed has no file for the period (404)."""
        cache = self.cache_dir / side / f"{period:%Y%m%d}.bi5"
        missing = cache.with_suffix(".404")
        if cache.exists():
            return cache.read_bytes()
        if missing.exists() and not self._is_recent(period):
            return None
        for attempt in range(self.retries):
            try:
                self._pace()
                blob = self._fetch(self.url_for(period, side))
                cache.parent.mkdir(parents=True, exist_ok=True)
                if not self._is_recent(period):  # the current period is still being written: do not cache
                    cache.write_bytes(blob)
                return blob
            except DataNotFound:
                cache.parent.mkdir(parents=True, exist_ok=True)
                missing.touch()
                return None
            except RateLimited as exc:  # the feed throttles bursts: back off and retry
                if attempt == self.retries - 1:
                    raise
                # Observed behaviour: no Retry-After header, and ~12 s of penalty after a 429.
                time.sleep(max(exc.retry_after or 0.0, 15.0 * (attempt + 1)))
            except DataUnavailableError:  # resets/aborted tunnels cluster when the feed throttles: wait longer
                if attempt == self.retries - 1:
                    raise
                time.sleep(10.0 * (attempt + 1))
        return None

    def _pace(self) -> None:
        if self.min_interval <= 0:
            return
        with self._pace_lock:
            now = time.monotonic()
            wait = self._next_slot - now
            self._next_slot = max(now, self._next_slot) + self.min_interval
        if wait > 0:
            time.sleep(wait)

    def _is_recent(self, period: datetime) -> bool:
        now = datetime.now(UTC)
        if self.granularity == "day":
            return period.year >= now.year
        if self.granularity == "hour":
            return (period.year, period.month) >= (now.year, now.month)
        return period.date() >= now.date()

    def _side(self, side: str, periods: list[datetime]) -> pd.DataFrame:
        failed: list[str] = []

        def get(p: datetime) -> bytes | None:
            try:
                return self._blob(p, side)
            except DataUnavailableError as exc:  # keep going; report every failed period at the end
                failed.append(f"{p.date()}: {str(exc)[:80]}")
                return None
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            blobs = list(pool.map(get, periods))
        if failed:
            raise DataUnavailableError(f"Dukascopy {side}: {len(failed)} period(s) could not be downloaded after "
                                       f"retries (everything else is cached; re-run to resume): {sorted(failed)[:5]}")
        frames = [decode_candles(b, p, self.point) for p, b in zip(periods, blobs, strict=True) if b]
        self.provenance[f"{side.lower()}_files"] = sum(b is not None for b in blobs)
        self.provenance[f"{side.lower()}_missing_periods"] = [str(p.date()) for p, b in zip(periods, blobs, strict=True)
                                                              if b is None][:50]
        df = pd.concat(frames).sort_index() if frames else pd.DataFrame()
        check_candles(df, side, self.expected_range)
        return df

    def fetch_series(self) -> pd.DataFrame:
        periods = list(self.periods())
        if not periods:
            raise ConfigError("empty date range")
        # Probe one period first so a blocked host fails fast with a clear message.
        try:
            self._blob(periods[0], "BID")
        except DataUnavailableError as exc:
            raise DataUnavailableError(f"Dukascopy datafeed unreachable ({exc}). If this is a 403 from the proxy, "
                                       "add datafeed.dukascopy.com to the environment's allowed domains.") from exc
        t0 = time.time()
        bid, ask = self._side("BID", periods), self._side("ASK", periods)
        if bid.empty:
            raise DataUnavailableError(f"no Dukascopy candles for {self.instrument} {self.start}..{self.end}")
        both = bid.join(ask, lsuffix="_bid", rsuffix="_ask", how="inner")
        live = (both["volume_bid"] > 0) | (both["volume_ask"] > 0)
        flat = int((~live).sum())
        both = both[live]
        both = both[(both.index >= self.start) & (both.index < self.end)]
        mid = pd.DataFrame({c: (both[f"{c}_bid"] + both[f"{c}_ask"]) / 2 for c in ["open", "high", "low", "close"]})
        mid["volume"] = both["volume_bid"]
        mid["spread"] = ((both["open_ask"] - both["open_bid"]) + (both["close_ask"] - both["close_bid"])) / 2
        neg = int((mid["spread"] < 0).sum())
        if neg > 0.001 * len(mid):
            raise DataQualityError(f"{neg} bars with ask < bid: BID/ASK files inconsistent")
        mid.index = mid.index + GRANULARITY[self.granularity][1]  # stamp at bar close (decision time)
        mid.index.name = "timestamp"
        self.provenance.update({"bars": int(len(mid)), "flat_zero_volume_dropped": flat,
                                "spread_median": float(mid["spread"].median()),
                                "volume": "Dukascopy tick volume (not exchange volume)",
                                "seconds": round(time.time() - t0, 1), "field_order": "open,close,low,high (verified by checks)"})
        log.info("Dukascopy %s %s: %d bars, %d flat filler candles dropped, median spread %.6f",
                 self.instrument, self.granularity, len(mid), flat, mid["spread"].median())
        return mid
