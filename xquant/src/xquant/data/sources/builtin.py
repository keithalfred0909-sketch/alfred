"""Built-in data sources.

Reachability from the development container (checked 2026-10-03): ``raw.githubusercontent.com`` is
allowed; Dukascopy, FRED, ECB, Yahoo, Stooq, BLS and GDELT are blocked by the network policy. The
connectors for blocked hosts are implemented against their documented public formats and become usable
as soon as the host is allowed (or when run on a normal machine).
"""

from __future__ import annotations

import hashlib
import io
import json
import lzma
import struct
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

from xquant.data.sources.base import CACHE_DIR, DATASETS_DIR, DataSource, FetchFn, register
from xquant.errors import ConfigError, DataNotFound, DataQualityError, DataUnavailableError, RateLimited
from xquant.logging_utils import get_logger

log = get_logger("data.sources")


def http_get(url: str, timeout: float = 60.0, session: requests.Session | None = None) -> bytes:
    try:
        getter = session.get if session is not None else requests.get
        resp = getter(url, timeout=timeout, headers={"User-Agent": "xquant-research/0.1"})
    except requests.RequestException as exc:
        raise DataUnavailableError(f"cannot reach {url}: {exc}") from exc
    if resp.status_code == 404:
        raise DataNotFound(f"{url} returned HTTP 404")
    if resp.status_code in (429, 503):  # throttled / temporarily unavailable: caller should back off
        ra = resp.headers.get("Retry-After")
        raise RateLimited(f"{url} returned HTTP {resp.status_code}", float(ra) if ra and ra.replace(".", "", 1).isdigit() else None)
    if resp.status_code != 200:
        raise DataUnavailableError(f"{url} returned HTTP {resp.status_code}")
    return resp.content


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@register
class HttpCsvSource(DataSource):
    """A CSV over HTTP(S) with one value column, optionally filtered by a category column.

    The filtered (date, value) table is persisted as a snapshot in ``datasets/`` together with a
    provenance sidecar (URL, raw-file sha256, download time). Later runs can be pinned to the snapshot
    with ``offline: true`` for exact reproducibility; if the network is unavailable the snapshot is
    used and the fallback is logged.
    """

    kind = "datahub_csv"

    def __init__(self, url: str, date_col: str, value_col: str, filter_col: str | None = None,
                 filter_value: str | None = None, snapshot: str | None = None, offline: bool = False,
                 orientation_anchor: dict[str, Any] | None = None, fetch: FetchFn | None = None,
                 datasets_dir: Path | None = None, **extra: Any) -> None:
        super().__init__(url=url, value_col=value_col, filter_value=filter_value, **extra)
        self.url, self.date_col, self.value_col = url, date_col, value_col
        self.filter_col, self.filter_value = filter_col, filter_value
        self.offline = offline
        self.anchor = orientation_anchor
        self._fetch = fetch or http_get
        self.datasets_dir = datasets_dir or DATASETS_DIR
        self.snapshot_path = self.datasets_dir / snapshot if snapshot else None
        self.provenance: dict[str, Any] = {}

    def _download(self) -> pd.DataFrame:
        raw = self._fetch(self.url)
        df = pd.read_csv(io.BytesIO(raw))
        for col in [self.date_col, self.value_col] + ([self.filter_col] if self.filter_col else []):
            if col not in df.columns:
                raise DataQualityError(f"{self.url}: expected column '{col}', found {list(df.columns)}")
        if self.filter_col:
            df = df[df[self.filter_col] == self.filter_value]
            if df.empty:
                raise DataQualityError(f"{self.url}: no rows with {self.filter_col}={self.filter_value}")
        out = pd.DataFrame({"date": df[self.date_col].astype(str),
                            "value": pd.to_numeric(df[self.value_col], errors="coerce")})
        self.provenance = {"url": self.url, "raw_sha256": _sha256(raw), "rows": int(len(out)),
                           "downloaded_at": datetime.now(UTC).isoformat(timespec="seconds"),
                           "filter": {self.filter_col: self.filter_value} if self.filter_col else None}
        if self.snapshot_path:
            self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            out.to_csv(self.snapshot_path, index=False)
            self.provenance["snapshot_sha256"] = _sha256(self.snapshot_path.read_bytes())
            self.snapshot_path.with_suffix(".meta.json").write_text(json.dumps(self.provenance, indent=2))
        return out

    def _load_snapshot(self, reason: str) -> pd.DataFrame:
        if not self.snapshot_path or not self.snapshot_path.exists():
            raise DataUnavailableError(f"{reason}; no snapshot available for {self.url}")
        log.warning("using snapshot %s (%s)", self.snapshot_path.name, reason)
        meta_path = self.snapshot_path.with_suffix(".meta.json")
        self.provenance = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        self.provenance["used_snapshot"] = True
        return pd.read_csv(self.snapshot_path, dtype={"date": str})

    def fetch_series(self) -> pd.DataFrame:
        if self.offline:
            df = self._load_snapshot("offline mode")
        else:
            try:
                df = self._download()
            except DataUnavailableError as exc:
                df = self._load_snapshot(str(exc))
        ts = pd.to_datetime(df["date"], errors="coerce")
        out = pd.DataFrame({"value": df["value"].to_numpy()}, index=pd.DatetimeIndex(ts, name="timestamp"))
        out = out[out.index.notna()]
        return self._orient(out)

    def _orient(self, df: pd.DataFrame) -> pd.DataFrame:
        """Verify quote orientation against a known anchor value; invert only if the check demands it."""
        if not self.anchor:
            return df
        d, ref, tol = pd.Timestamp(self.anchor["date"]), float(self.anchor["value"]), float(
            self.anchor.get("tolerance", 0.002))
        if d not in df.index or pd.isna(df.loc[d, "value"]):
            raise DataQualityError(f"orientation anchor date {d.date()} missing in {self.url}")
        v = float(df.loc[d, "value"])  # type: ignore[arg-type]
        if abs(v - ref) <= tol:
            self.provenance["orientation"] = "as published"
            return df
        if v != 0 and abs(1.0 / v - ref) <= tol:
            log.info("orientation check: %s on %s is %.4f, anchor %.4f -> series inverted", self.url,
                     d.date(), v, ref)
            self.provenance["orientation"] = f"inverted (published {v} on {d.date()}, anchor {ref})"
            return df.assign(value=1.0 / df["value"])
        raise DataQualityError(f"orientation anchor mismatch: {v} vs {ref} (or its inverse) on {d.date()}")


@register
class CsvFileSource(DataSource):
    """Local OHLCV CSV. Columns are matched case-insensitively; a ``columns`` mapping may rename them."""

    kind = "csv_file"

    def __init__(self, path: str, timestamp_col: str = "timestamp", tz: str = "UTC",
                 columns: dict[str, str] | None = None, **extra: Any) -> None:
        super().__init__(path=path, tz=tz, **extra)
        self.path = self.resolve_path(path)
        self.timestamp_col, self.tz, self.columns = timestamp_col, tz, columns or {}

    def fetch_series(self) -> pd.DataFrame:
        if not self.path.exists():
            raise DataUnavailableError(f"CSV file not found: {self.path}")
        df = pd.read_csv(self.path)
        df = df.rename(columns=self.columns)
        df.columns = [str(c).strip().lower() for c in df.columns]
        tcol = self.timestamp_col.lower()
        if tcol not in df.columns:
            raise DataQualityError(f"{self.path}: timestamp column '{tcol}' not found")
        ts = pd.to_datetime(df.pop(tcol), errors="coerce", utc=False)
        idx = pd.DatetimeIndex(ts, name="timestamp")
        if idx.tz is None:
            idx = idx.tz_localize(self.tz, ambiguous="NaT", nonexistent="NaT")
        df.index = idx
        keep = [c for c in ["open", "high", "low", "close", "volume", "value", "spread"] if c in df.columns]
        if not keep:
            raise DataQualityError(f"{self.path}: no recognised price columns")
        return df[keep].apply(pd.to_numeric, errors="coerce")


@register
class DukascopySource(DataSource):
    """Dukascopy historical tick feed (public). Hourly LZMA-compressed ``.bi5`` files of 20-byte records:
    uint32 ms-from-hour, uint32 ask, uint32 bid, float32 ask volume, float32 bid volume (big-endian).
    Months in the URL are zero-based. Prices are integers in units of ``point``. Timestamps are UTC.
    Ticks are aggregated into bars on the mid price; the mean spread per bar is kept.
    """

    kind = "dukascopy"
    BASE = "https://datafeed.dukascopy.com/datafeed"

    def __init__(self, instrument: str, start: str, end: str, point: float = 1e-5, bar: str = "1h",
                 fetch: FetchFn | None = None, cache_dir: Path | None = None, **extra: Any) -> None:
        super().__init__(instrument=instrument, start=start, end=end, point=point, bar=bar)
        self.instrument, self.point, self.bar = instrument.upper(), point, bar
        self.start, self.end = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
        self._fetch = fetch or http_get
        self.cache_dir = (cache_dir or CACHE_DIR) / "dukascopy" / self.instrument

    def url_for(self, hour: datetime) -> str:
        return f"{self.BASE}/{self.instrument}/{hour.year}/{hour.month - 1:02d}/{hour.day:02d}/{hour.hour:02d}h_ticks.bi5"

    @staticmethod
    def decode_bi5(blob: bytes, hour: datetime, point: float) -> pd.DataFrame:
        if not blob:
            return pd.DataFrame(columns=["ask", "bid", "ask_vol", "bid_vol"])
        raw = lzma.decompress(blob)
        if len(raw) % 20:
            raise DataQualityError(f"corrupt bi5 payload for {hour}: {len(raw)} bytes")
        recs = np.array(list(struct.iter_unpack(">IIIff", raw)))
        base = pd.Timestamp(hour).tz_convert("UTC") if pd.Timestamp(hour).tzinfo else pd.Timestamp(hour, tz="UTC")
        idx = base + pd.to_timedelta(recs[:, 0], unit="ms")
        return pd.DataFrame({"ask": recs[:, 1] * point, "bid": recs[:, 2] * point,
                             "ask_vol": recs[:, 3], "bid_vol": recs[:, 4]}, index=pd.DatetimeIndex(idx, name="timestamp"))

    def _hour_blob(self, hour: datetime) -> bytes:
        cache = self.cache_dir / f"{hour:%Y%m%d%H}.bi5"
        if cache.exists():
            return cache.read_bytes()
        blob = self._fetch(self.url_for(hour))
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(blob)
        return blob

    def fetch_series(self) -> pd.DataFrame:
        frames = []
        hour = self.start.to_pydatetime()
        end = self.end.to_pydatetime()
        while hour < end:
            if hour.weekday() != 5:  # FX is closed all Saturday (UTC); skip obvious empty hours
                frames.append(self.decode_bi5(self._hour_blob(hour), hour, self.point))
            hour += timedelta(hours=1)
        ticks = pd.concat([f for f in frames if not f.empty]) if frames else pd.DataFrame()
        if ticks.empty:
            raise DataUnavailableError(f"no Dukascopy ticks for {self.instrument} {self.start}..{self.end}")
        mid = (ticks["ask"] + ticks["bid"]) / 2
        g = mid.resample(self.bar, label="right", closed="left")
        bars = pd.DataFrame({"open": g.first(), "high": g.max(), "low": g.min(), "close": g.last(),
                             "volume": (ticks["ask_vol"] + ticks["bid_vol"]).resample(self.bar, label="right", closed="left").sum(),
                             "spread": (ticks["ask"] - ticks["bid"]).resample(self.bar, label="right", closed="left").mean()})
        return bars.dropna(subset=["close"])


@register
class FredSource(DataSource):
    """FRED public CSV endpoint (no API key). Missing observations are encoded as '.'."""

    kind = "fred"

    def __init__(self, series_id: str, fetch: FetchFn | None = None, **extra: Any) -> None:
        super().__init__(series_id=series_id)
        self.series_id = series_id
        self._fetch = fetch or http_get

    def fetch_series(self) -> pd.DataFrame:
        raw = self._fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={self.series_id}")
        df = pd.read_csv(io.BytesIO(raw), na_values=["."])
        date_col = "observation_date" if "observation_date" in df.columns else df.columns[0]
        if self.series_id not in df.columns:
            raise DataQualityError(f"FRED CSV for {self.series_id} has columns {list(df.columns)}")
        return pd.DataFrame({"value": pd.to_numeric(df[self.series_id], errors="coerce").to_numpy()},
                            index=pd.DatetimeIndex(pd.to_datetime(df[date_col]), name="timestamp"))


EVENT_COLUMNS = ["timestamp", "event", "country", "currency", "importance", "previous", "consensus", "actual"]


@register
class EconCalendarCsvSource(DataSource):
    """Economic calendar with expectations. Required columns: ``EVENT_COLUMNS``; timestamps must carry a
    timezone or ``tz`` must be given. Rows without consensus are kept but cannot produce a surprise."""

    kind = "econ_calendar_csv"

    def __init__(self, path: str, tz: str = "UTC", **extra: Any) -> None:
        super().__init__(path=path, tz=tz)
        self.path, self.tz = self.resolve_path(path), tz

    def fetch_series(self) -> pd.DataFrame:
        if not self.path.exists():
            raise DataUnavailableError(f"economic calendar file not found: {self.path}")
        df = pd.read_csv(self.path)
        missing = [c for c in EVENT_COLUMNS if c not in df.columns]
        if missing:
            raise DataQualityError(f"calendar missing columns {missing}")
        ts = pd.DatetimeIndex(pd.to_datetime(df.pop("timestamp")))
        df.index = (ts.tz_localize(self.tz) if ts.tz is None else ts).tz_convert("UTC").rename("timestamp")
        for c in ["previous", "consensus", "actual"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df.sort_index()


NEWS_COLUMNS = ["timestamp", "source", "headline"]


@register
class NewsCsvSource(DataSource):
    """Timestamped news items. Required: ``NEWS_COLUMNS``; optional: body, url, asset, country."""

    kind = "news_csv"

    def __init__(self, path: str, tz: str = "UTC", **extra: Any) -> None:
        super().__init__(path=path, tz=tz)
        self.path, self.tz = self.resolve_path(path), tz

    def fetch_series(self) -> pd.DataFrame:
        if not self.path.exists():
            raise DataUnavailableError(f"news file not found: {self.path}")
        df = pd.read_csv(self.path)
        missing = [c for c in NEWS_COLUMNS if c not in df.columns]
        if missing:
            raise DataQualityError(f"news file missing columns {missing}")
        ts = pd.DatetimeIndex(pd.to_datetime(df.pop("timestamp")))
        df.index = (ts.tz_localize(self.tz) if ts.tz is None else ts).tz_convert("UTC").rename("timestamp")
        return df.sort_index()


def parse_date(s: str | date) -> date:
    if isinstance(s, date):
        return s
    try:
        return date.fromisoformat(s)
    except ValueError as exc:
        raise ConfigError(f"bad date {s!r}") from exc


# Additional sources live in their own modules; importing them here registers them.
from xquant.data.sources import dukascopy_candles, mt5, resample  # noqa: E402,F401
