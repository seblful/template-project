"""Shared pytest fixtures for demo-proj."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import BaseModel

from demo_proj.logging import reset_logging
from demo_proj.settings import Settings, load_settings

# Built from the model rather than listed, so a field added later is cleared too.
# Keys are upper-cased first because settings match env vars case-insensitively.
_PREFIX = Settings.model_config.get("env_prefix", "").upper()
_ENV_NAMES = tuple(f"{_PREFIX}{name.upper()}" for name in Settings.model_fields)
_ENV_PREFIXES = tuple(f"{name}__" for name in _ENV_NAMES)


@pytest.fixture(autouse=True)
def _isolated_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear top-level and whole-group values as well as nested variables."""
    for key in list(os.environ):
        if key.upper() in _ENV_NAMES or key.upper().startswith(_ENV_PREFIXES):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _isolated_logging() -> Iterator[None]:
    """Detach any handler a test installed."""
    yield
    reset_logging()


@pytest.fixture
def supported_keys() -> set[str]:
    """Return every variable name the model reads, groups expanded to their fields."""
    keys = set()
    for name, field in Settings.model_fields.items():
        group = field.annotation
        if isinstance(group, type) and issubclass(group, BaseModel):
            keys.update(f"{name}__{nested}" for nested in group.model_fields)
        else:
            keys.add(name)
    return {f"{_PREFIX}{key.upper()}" for key in keys}


@pytest.fixture
def tmp_env_file(tmp_path: Path) -> Path:
    """Create a temporary .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DEMO_PROJ_LOGGING__FORMAT=json\n",
        encoding="utf-8",
    )
    return env_file


@pytest.fixture
def test_settings(tmp_env_file: Path) -> Settings:
    """Load settings from a temporary env file instead of the project's."""
    return load_settings(env_file=tmp_env_file)
