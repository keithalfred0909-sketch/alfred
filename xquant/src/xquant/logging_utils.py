"""Structured logging: human-readable on the console, JSON lines in the run directory."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

_CONFIGURED = False


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extra = getattr(record, "data", None)
        if extra:
            payload["data"] = extra
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    """Idempotent logging setup. Safe to call from CLI and from tests."""
    global _CONFIGURED
    root = logging.getLogger("xquant")
    root.setLevel(level.upper())
    if not _CONFIGURED:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(name)s | %(message)s", "%H:%M:%S"))
        root.addHandler(console)
        root.propagate = False
        _CONFIGURED = True
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        if not any(isinstance(h, logging.FileHandler) and Path(h.baseFilename) == log_file.resolve()
                   for h in root.handlers):
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(JsonLineFormatter())
            root.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"xquant.{name}")
