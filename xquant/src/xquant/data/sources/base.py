"""Data source interface and registry.

A source returns *raw* data in a documented shape; cleaning and validation happen in the engine so that
every source gets the same treatment. Sources that cannot be reached raise ``DataUnavailableError`` -
they never return placeholder data.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd

from xquant.config import PROJECT_ROOT
from xquant.errors import ConfigError

DATASETS_DIR = PROJECT_ROOT / "datasets"
CACHE_DIR = PROJECT_ROOT / "cache"


class DataSource(ABC):
    """Abstract source. ``kind`` is the key used in configuration files."""

    kind: ClassVar[str]

    def __init__(self, **params: Any) -> None:
        self.params = params

    @abstractmethod
    def fetch_series(self) -> pd.DataFrame:
        """Return a DataFrame with a naive or tz-aware ``timestamp`` index and source columns.

        Price sources return columns among open/high/low/close/volume (missing ones may be absent).
        Scalar series sources return a single ``value`` column.
        """

    def describe(self) -> str:
        return f"{self.kind}({', '.join(f'{k}={v}' for k, v in self.params.items() if k != 'session')})"

    def resolve_path(self, p: str | Path) -> Path:
        path = Path(p)
        return path if path.is_absolute() else PROJECT_ROOT / path


_REGISTRY: dict[str, type[DataSource]] = {}


def register(cls: type[DataSource]) -> type[DataSource]:
    if cls.kind in _REGISTRY:
        raise ConfigError(f"duplicate data source kind {cls.kind}")
    _REGISTRY[cls.kind] = cls
    return cls


def build_source(kind: str, params: dict[str, Any]) -> DataSource:
    # Import side effect registers built-in sources.
    from xquant.data.sources import builtin  # noqa: F401

    if kind not in _REGISTRY:
        raise ConfigError(f"unknown data source kind '{kind}'. Registered: {sorted(_REGISTRY)}")
    return _REGISTRY[kind](**params)


def registered_kinds() -> list[str]:
    from xquant.data.sources import builtin  # noqa: F401

    return sorted(_REGISTRY)


FetchFn = Callable[[str], bytes]
