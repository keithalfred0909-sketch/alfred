import importlib

import abogado

MODULES = [
    "domain", "llm", "pipeline", "sources", "verification",
    "deadlines", "documents", "drafting", "storage", "cli",
]


def test_version():
    assert abogado.__version__


def test_modules_importable():
    for name in MODULES:
        importlib.import_module(f"abogado.{name}")
