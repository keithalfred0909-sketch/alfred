"""DATA ENGINE: load, clean, validate and version everything a research run consumes."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from xquant.config import AssetSpec, MacroSeriesSpec
from xquant.data.cleaning import QualityReport, clean_bars
from xquant.data.pit import align_point_in_time, transform_series
from xquant.data.schema import DatasetMeta, frame_sha256, infer_capabilities, validate_bars
from xquant.data.sources.base import build_source
from xquant.errors import DataQualityError, DataUnavailableError
from xquant.logging_utils import get_logger

log = get_logger("data.engine")


@dataclass
class MarketDataset:
    bars: pd.DataFrame
    meta: DatasetMeta
    quality: QualityReport
    exog: pd.DataFrame = field(default_factory=pd.DataFrame)  # point-in-time aligned on bars.index
    exog_meta: dict[str, dict[str, Any]] = field(default_factory=dict)
    events: pd.DataFrame | None = None  # economic calendar (UTC index)
    news: pd.DataFrame | None = None

    @property
    def version(self) -> str:
        """Dataset version = hash of bars + exogenous inputs. Changes => memory may revisit hypotheses."""
        parts = [self.meta.sha256] + [f"{k}:{m.get('sha256', '')}" for k, m in sorted(self.exog_meta.items())]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]

    def summary(self) -> dict[str, Any]:
        return {"symbol": self.meta.symbol, "timeframe": self.meta.timeframe, "rows": self.meta.n_rows,
                "start": self.meta.start, "end": self.meta.end, "capabilities": self.meta.capabilities.describe(),
                "quality": self.quality.verdict, "exogenous": sorted(self.exog.columns),
                "events": 0 if self.events is None else len(self.events),
                "news": 0 if self.news is None else len(self.news), "version": self.version}


class DataEngine:
    def __init__(self, asset: AssetSpec, offline: bool = False) -> None:
        self.asset = asset
        self.offline = offline

    def _source_params(self, params: dict[str, Any]) -> dict[str, Any]:
        p = dict(params)
        if self.offline and "url" in p:
            p["offline"] = True
        return p

    def load_bars(self) -> tuple[pd.DataFrame, DatasetMeta, QualityReport]:
        spec = self.asset.price_source
        src = build_source(spec.kind, self._source_params(spec.params))
        raw = src.fetch_series()
        bars, rep = clean_bars(raw, tz=self.asset.timezone, timeframe=self.asset.timeframe,
                               close_time=spec.params.get("close_time"))
        if rep.verdict == "FAIL":
            raise DataQualityError(f"{self.asset.symbol}: data quality FAIL: {rep.notes}")
        validate_bars(bars)
        caps = infer_capabilities(bars, self.asset.timeframe)
        notes = []
        prov = getattr(src, "provenance", {})
        if prov:
            notes.append(f"provenance: {prov}")
        if not caps.ohlc:
            notes.append("close-only data: no open/high/low; intrabar stops and range features unavailable")
        if not caps.volume:
            notes.append("no volume data")
        if "spread" in bars.columns and bars["spread"].notna().any():
            notes.append(f"per-bar spread available (median {bars['spread'].median():.6g})")
        if self.asset.cross_check:
            cc = self.cross_check(bars)
            notes.append(f"cross-check vs {self.asset.cross_check.get('asset')}: {cc}")
        meta = DatasetMeta(symbol=self.asset.symbol, timeframe=self.asset.timeframe, source=src.describe(),
                           sha256=frame_sha256(bars), capabilities=caps, n_rows=len(bars),
                           start=str(bars.index[0]), end=str(bars.index[-1]), notes=notes)
        log.info("loaded %s: %d bars %s..%s (%s), quality %s", self.asset.symbol, len(bars),
                 bars.index[0].date(), bars.index[-1].date(), caps.describe(), rep.verdict)
        return bars, meta, rep

    def cross_check(self, bars: pd.DataFrame) -> dict[str, Any]:
        """Validate the price source against an independent reference asset config (raises on failure)."""
        from xquant.config import load_config
        from xquant.data.crosscheck import cross_check_daily
        cc = dict(self.asset.cross_check or {})
        if cc.pop("kind", "daily_fixing") == "monthly_mean":
            from xquant.data.crosscheck import cross_check_monthly_mean
            src = build_source(cc["source"]["kind"], {**cc["source"]["params"], "offline": True})
            return cross_check_monthly_mean(bars, src.fetch_series()["value"],
                                            **{k: v for k, v in cc.items() if k not in ("source", "asset")})
        ref_cfg = load_config(str(cc.pop("asset")))
        ref_bars, _, _ = DataEngine(ref_cfg.asset, offline=True).load_bars()
        return cross_check_daily(bars, ref_bars["close"], **cc)

    def load_exogenous(self, bar_index: pd.DatetimeIndex) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
        cols: dict[str, pd.Series] = {}
        metas: dict[str, dict[str, Any]] = {}
        specs: list[MacroSeriesSpec] = list(self.asset.macro) + list(self.asset.cross_assets)
        for spec in specs:
            try:
                src = build_source(spec.source.kind, self._source_params(spec.source.params))
                raw = src.fetch_series()["value"]
            except (DataUnavailableError, DataQualityError) as exc:
                log.warning("exogenous series %s unavailable: %s", spec.name, exc)
                metas[spec.name] = {"status": "UNAVAILABLE", "reason": str(exc)}
                continue
            raw.index = pd.DatetimeIndex(raw.index)
            stz = spec.timezone or self.asset.timezone
            if raw.index.tz is not None:
                raw.index = raw.index.tz_convert(stz).tz_localize(None)
            series = transform_series(raw.astype("float64"), spec.transform, spec.frequency)
            aligned = align_point_in_time(series.rename(spec.name), bar_index, spec.frequency,
                                          spec.availability_lag_days, tz=stz)
            cols[spec.name] = aligned
            metas[spec.name] = {"status": "OK", "frequency": spec.frequency, "lag_days": spec.availability_lag_days,
                                "transform": spec.transform, "source": src.describe(),
                                "provenance": getattr(src, "provenance", {}),
                                "first_available": str(aligned.first_valid_index()),
                                "coverage": float(aligned.notna().mean()),
                                "sha256": frame_sha256(aligned.to_frame()), "description": spec.description}
        exog = pd.DataFrame(cols, index=bar_index)
        return exog, metas

    def load_optional(self, which: str) -> pd.DataFrame | None:
        spec = self.asset.calendar_source if which == "calendar" else self.asset.news_source
        if spec is None:
            return None
        try:
            return build_source(spec.kind, spec.params).fetch_series()
        except (DataUnavailableError, DataQualityError) as exc:
            log.warning("%s source unavailable: %s", which, exc)
            return None

    def load(self) -> MarketDataset:
        bars, meta, rep = self.load_bars()
        exog, exog_meta = self.load_exogenous(pd.DatetimeIndex(bars.index))
        return MarketDataset(bars=bars, meta=meta, quality=rep, exog=exog, exog_meta=exog_meta,
                             events=self.load_optional("calendar"), news=self.load_optional("news"))
