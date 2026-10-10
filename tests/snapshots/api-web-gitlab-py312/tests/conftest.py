"""Shared pytest fixtures for demo-proj."""

import os
from collections.abc import Iterator

import pytest

from demo_proj.logging import reset_logging
from demo_proj.settings import Settings

_PREFIX = Settings.model_config.get("env_prefix", "").upper()


@pytest.fixture(autouse=True)
def _isolated_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear every variable the settings could read from the host."""
    for key in list(os.environ):
        if key.upper().startswith(_PREFIX):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _isolated_logging() -> Iterator[None]:
    """Detach any handler a test installed."""
    yield
    reset_logging()
