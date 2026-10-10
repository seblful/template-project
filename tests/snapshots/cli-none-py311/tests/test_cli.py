"""End-to-end tests for the CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from demo_proj import __version__
from demo_proj.cli import app
from demo_proj.logging import reset_logging

runner = CliRunner()


def test_settings_command_prints_the_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`settings` prints the defaults as JSON and leaves the working dir untouched."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["settings"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"logging": {"format": "text", "level": "INFO"}}
    assert list(tmp_path.iterdir()) == []


def test_version_flag_works_without_a_subcommand() -> None:
    """`--version` does not trip over no_args_is_help or "Missing command"."""
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_bare_invocation_shows_help() -> None:
    """No arguments prints help rather than failing."""
    result = runner.invoke(app, [])

    assert "Usage:" in result.output


def test_module_is_executable(tmp_path: Path) -> None:
    """`python -m demo_proj` is a working entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "demo_proj", "--version"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert __version__ in result.stdout


def test_cli_loads_an_explicit_file_for_each_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--env-file` applies to its own run only; a `.env` in the cwd is never read."""
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / "selected.env"
    env_file.write_text(
        "LOGGING__FORMAT=json\nLOGGING__LEVEL=DEBUG\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text("LOGGING__FORMAT=invalid\n", encoding="utf-8")

    assert runner.invoke(app, ["settings"]).exit_code == 0
    reset_logging()
    selected = runner.invoke(app, ["--env-file", str(env_file), "settings"])
    reset_logging()
    default = runner.invoke(app, ["settings"])

    assert selected.exit_code == 0, selected.output
    assert json.loads(selected.stderr)["event"] == "showing settings"
    assert json.loads(selected.stdout)["logging"] == {
        "format": "json",
        "level": "DEBUG",
    }
    assert default.exit_code == 0, default.output
    assert json.loads(default.stdout)["logging"]["level"] == "INFO"
    assert default.stderr == ""


def test_cli_rejects_a_missing_env_file(tmp_path: Path) -> None:
    """A missing path is a usage error, reported before any command runs."""
    result = runner.invoke(app, ["--env-file", str(tmp_path / "absent"), "settings"])

    assert result.exit_code == 2


@pytest.mark.parametrize("args", [["--version"], ["settings", "--help"]])
def test_version_and_help_do_not_load_settings(
    args: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invalid configuration cannot break `--version` or a subcommand's `--help`."""
    monkeypatch.setenv("LOGGING__FORMAT", "invalid")

    result = runner.invoke(app, args)

    assert result.exit_code == 0, result.output
