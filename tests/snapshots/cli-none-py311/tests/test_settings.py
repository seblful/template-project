"""Tests for application settings."""

import re
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from demo_proj.settings import Settings


def _supported_keys() -> set[str]:
    """Return every variable name the model reads, groups expanded to their fields."""
    prefix = Settings.model_config.get("env_prefix", "")
    keys = set()
    for name, field in Settings.model_fields.items():
        group = field.annotation
        if isinstance(group, type) and issubclass(group, BaseModel):
            keys.update(f"{name}__{nested}" for nested in group.model_fields)
        else:
            keys.add(name)
    return {f"{prefix}{key}".upper() for key in keys}


def test_committed_env_example_matches_the_settings_model() -> None:
    """The example lists every supported field, no obsolete keys, and valid values."""
    example = Path(__file__).resolve().parents[1] / ".env.example"
    actual = set()
    for raw in example.read_text(encoding="utf-8").splitlines():
        # Commented-out keys count: they document optional fields.
        key = raw.strip().lstrip("#").strip().split("=", 1)
        if len(key) == 2 and re.fullmatch(r"[A-Z][A-Z0-9_]*", key[0].strip()):
            actual.add(key[0].strip())

    assert actual == _supported_keys()
    Settings(_env_file=example)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("DEMO_PROJ_LOGGING__FORMA", "json"),
        ("DEMO_PROJ_LOGGING__FORMAT", "invalid"),
    ],
    ids=["unknown-field", "invalid-value"],
)
def test_invalid_settings_are_rejected(
    name: str, value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A typo or a bad value inside a settings group fails loudly at startup."""
    monkeypatch.setenv(name, value)

    with pytest.raises(ValidationError, match="logging"):
        Settings()


def test_level_is_accepted_in_any_letter_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`debug` is normalized to the canonical `DEBUG` instead of being rejected."""
    monkeypatch.setenv("DEMO_PROJ_LOGGING__LEVEL", "debug")

    assert Settings().logging.level == "DEBUG"
