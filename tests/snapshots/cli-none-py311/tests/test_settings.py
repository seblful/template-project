"""Unit tests for application settings."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from demo_proj.settings import Settings, load_settings


def test_settings_load_from_env_file(test_settings: Settings) -> None:
    """A selected dotenv file overrides its keys and leaves the rest at defaults."""
    assert test_settings.logging.format == "json"
    assert test_settings.logging.level == "INFO"


def test_unrelated_env_file_keys_are_ignored(tmp_path: Path) -> None:
    """Keys that match no settings field belong to other tools and pass silently."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DEMO_PROJ_LOGGING__FORMAT=json\nDATABASE_URL=postgres://db\n",
        encoding="utf-8",
    )

    assert load_settings(env_file=env_file).logging.format == "json"


@pytest.mark.parametrize(
    "entry",
    [
        "DEMO_PROJ_LOGGING__FORMA=json",
        "DEMO_PROJ_LOGGING__FORMAT=invalid",
    ],
    ids=["unknown-field", "invalid-value"],
)
def test_invalid_settings_are_rejected(tmp_path: Path, entry: str) -> None:
    """A typo or a bad value inside a settings group fails loudly at startup."""
    env_file = tmp_path / ".env"
    env_file.write_text(entry, encoding="utf-8")

    with pytest.raises(ValidationError, match="logging"):
        load_settings(env_file=env_file)


def test_settings_are_immutable(test_settings: Settings) -> None:
    """Loaded settings cannot be reassigned after startup."""
    with pytest.raises(ValidationError, match="frozen"):
        test_settings.logging.format = "text"  # ty: ignore[invalid-assignment]


def test_each_load_reads_the_current_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nothing is cached, so a later load sees a changed environment."""
    first = load_settings()
    monkeypatch.setenv("DEMO_PROJ_LOGGING__FORMAT", "json")

    assert first.logging.format == "text"
    assert load_settings().logging.format == "json"


def test_variables_without_the_package_prefix_are_not_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A generic name such as `LOGGING__FORMAT` belongs to someone else."""
    monkeypatch.setenv("LOGGING__FORMAT", "json")

    assert load_settings().logging.format == "text"


def test_level_is_accepted_in_any_letter_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`debug` is normalized to the canonical `DEBUG` instead of being rejected."""
    monkeypatch.setenv("DEMO_PROJ_LOGGING__LEVEL", "debug")

    assert load_settings().logging.level == "DEBUG"


def test_whole_group_json_and_nested_env_values_merge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A nested variable overrides the matching key of a whole-group JSON value."""
    monkeypatch.setenv(
        "DEMO_PROJ_LOGGING",
        '{"level":"DEBUG","format":"text"}',
    )
    monkeypatch.setenv("DEMO_PROJ_LOGGING__FORMAT", "json")

    settings = load_settings()

    assert settings.logging.level == "DEBUG"
    assert settings.logging.format == "json"


def test_defaults_are_isolated_from_the_host() -> None:
    """With the host's variables cleared, every field uses its declared default."""
    settings = load_settings()

    assert settings.logging.format == "text"
    assert settings.logging.level == "INFO"
