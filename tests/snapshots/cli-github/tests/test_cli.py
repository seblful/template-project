"""End-to-end tests for the CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from demo_proj import __version__
from demo_proj.cli import app

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


def test_settings_command_reads_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`settings` prints what the environment selects and logs in that format."""
    monkeypatch.setenv("DEMO_PROJ_LOGGING__FORMAT", "json")
    monkeypatch.setenv("DEMO_PROJ_LOGGING__LEVEL", "DEBUG")

    result = runner.invoke(app, ["settings"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stderr)["event"] == "showing settings"
    assert json.loads(result.stdout)["logging"] == {"format": "json", "level": "DEBUG"}


@pytest.mark.parametrize("args", [["--version"], ["settings", "--help"]])
def test_version_and_help_do_not_load_settings(
    args: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invalid configuration cannot break `--version` or a subcommand's `--help`."""
    monkeypatch.setenv("DEMO_PROJ_LOGGING__FORMAT", "invalid")

    result = runner.invoke(app, args)

    assert result.exit_code == 0, result.output
