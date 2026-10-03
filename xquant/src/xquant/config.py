"""Typed configuration. A research run is fully determined by (config, dataset hashes, code version, seed).

Configuration is layered: ``configs/default.yaml`` is overlaid by an asset file such as
``configs/assets/eurusd.yaml``. Switching asset never requires touching the core: only a new asset file.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator

from xquant.errors import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"


class SourceSpec(BaseModel):
    """Where a series comes from. ``kind`` selects a registered DataSource implementation."""

    kind: str
    params: dict[str, Any] = Field(default_factory=dict)


class MacroSeriesSpec(BaseModel):
    name: str
    source: SourceSpec
    frequency: Literal["daily", "monthly", "quarterly"]
    # Point-in-time availability. A value stamped at period P becomes usable only after this lag,
    # expressed against the *end* of P. Conservative defaults are preferred to optimistic ones.
    availability_lag_days: int = 0
    transform: Literal["level", "yoy", "diff"] = "level"
    description: str = ""


class CostModel(BaseModel):
    spread_bps: float = 1.0  # full bid/ask spread; half is paid on each fill
    commission_bps: float = 0.5  # per fill
    slippage_bps: float = 0.5  # per fill
    latency_bars: int = 0  # extra bars between signal and fill


class SplitSpec(BaseModel):
    train_end: date
    validation_end: date
    test_end: date
    # Bars dropped after each boundary so that features/labels computed with windows do not leak.
    embargo_bars: int = 20

    @model_validator(mode="after")
    def _ordered(self) -> SplitSpec:
        if not (self.train_end < self.validation_end < self.test_end):
            raise ValueError("splits must satisfy train_end < validation_end < test_end")
        return self


class AssetSpec(BaseModel):
    symbol: str
    name: str
    market: str
    timeframe: str  # pandas offset alias of the bar, e.g. "1D", "1h", "5min"
    timezone: str = "UTC"
    price_source: SourceSpec
    costs: CostModel = Field(default_factory=CostModel)
    splits: SplitSpec
    macro: list[MacroSeriesSpec] = Field(default_factory=list)
    cross_assets: list[MacroSeriesSpec] = Field(default_factory=list)
    calendar_source: SourceSpec | None = None
    news_source: SourceSpec | None = None


class BudgetSpec(BaseModel):
    max_experiments: int = 200
    max_generations: int = 25
    population: int = 120
    max_compute_minutes: float = 60.0
    max_strategies: int = 40
    max_complexity: int = 4
    max_features: int = 400
    max_hypotheses: int = 6000
    patience: int = 4  # generations without fitness improvement before an evolution line stops
    max_line_failures: int = 3


class StatsSpec(BaseModel):
    fdr_alpha: float = 0.05
    min_samples: int = 40
    min_trades: int = 30
    horizons: list[int] = Field(default_factory=lambda: [1, 3, 5, 10, 20])
    quantiles: list[float] = Field(default_factory=lambda: [0.1, 0.2, 0.8, 0.9])
    bootstrap_reps: int = 1000
    min_effect_size: float = 0.05  # |mean diff| / unconditional std of the forward return


class RobustnessSpec(BaseModel):
    param_perturbation: float = 0.25
    min_param_stability: float = 0.6  # fraction of perturbed neighbours that must stay profitable
    cost_stress_multipliers: list[float] = Field(default_factory=lambda: [2.0, 3.0])
    random_entry_reps: int = 500
    max_random_entry_pvalue: float = 0.05
    max_top_trade_share: float = 0.5  # share of total profit coming from the top 5% trades
    min_profitable_year_share: float = 0.5
    min_deflated_sharpe_prob: float = 0.95
    mc_reps: int = 1000
    wf_windows: int = 6
    noise_vol_fraction: float = 0.1
    max_pbo: float = 0.5


class ResearchSpec(BaseModel):
    seed: int = 42
    mode: Literal["standard", "deep", "quick"] = "standard"
    runs_dir: str = "runs"
    memory_path: str = "research_output/memory.db"


class XQuantConfig(BaseModel):
    asset: AssetSpec
    research: ResearchSpec = Field(default_factory=ResearchSpec)
    budgets: dict[str, BudgetSpec] = Field(default_factory=dict)
    stats: StatsSpec = Field(default_factory=StatsSpec)
    robustness: RobustnessSpec = Field(default_factory=RobustnessSpec)

    @property
    def budget(self) -> BudgetSpec:
        return self.budgets.get(self.research.mode, BudgetSpec())

    def fingerprint(self) -> str:
        """Stable hash of the full configuration, stored with every experiment."""
        blob = json.dumps(self.model_dump(mode="json"), sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def load_config(asset: str | Path, overrides: dict[str, Any] | None = None,
                default_path: Path | None = None) -> XQuantConfig:
    """Load default config and overlay the asset file.

    ``asset`` is either a path to a YAML file or a symbol resolved against ``configs/assets``
    (``EURUSD``, ``eur/usd`` and ``eurusd`` are equivalent).
    """
    default_path = default_path or CONFIG_DIR / "default.yaml"
    asset_path = Path(asset)
    if not asset_path.suffix:
        key = str(asset).lower().replace("/", "").replace("-", "").replace("_", "")
        asset_path = CONFIG_DIR / "assets" / f"{key}.yaml"
    if not asset_path.exists():
        available = sorted(p.stem.upper() for p in (CONFIG_DIR / "assets").glob("*.yaml"))
        raise ConfigError(f"No asset config at {asset_path}. Available: {available}")
    base = yaml.safe_load(default_path.read_text()) if default_path.exists() else {}
    merged = _deep_merge(base or {}, yaml.safe_load(asset_path.read_text()) or {})
    if overrides:
        merged = _deep_merge(merged, overrides)
    try:
        return XQuantConfig.model_validate(merged)
    except Exception as exc:  # pydantic.ValidationError, but keep the message intact
        raise ConfigError(f"Invalid configuration ({asset_path.name}): {exc}") from exc
