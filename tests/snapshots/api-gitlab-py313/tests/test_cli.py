"""End-to-end tests for the CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import uvicorn
from typer.testing import CliRunner

import demo_proj
from demo_proj import __version__
from demo_proj.cli import app

runner = CliRunner()


@pytest.fixture
def served(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Record what `serve` passes to uvicorn, instead of starting a server."""
    calls: dict[str, object] = {}

    def fake_run(application: str, **kwargs: object) -> None:
        calls.update(kwargs, application=application)

    monkeypatch.setattr(uvicorn, "run", fake_run)
    return calls


def test_serve_runs_the_app_with_logging_left_to_the_application(
    served: dict[str, object],
) -> None:
    """`serve` hands uvicorn the factory, the address, and no logging config."""
    result = runner.invoke(app, ["serve", "--port", "9000"])

    assert result.exit_code == 0, result.output
    assert served["application"] == "demo_proj.app:create_serving_app"
    assert served["factory"] is True
    assert served["host"] == "127.0.0.1"
    assert served["port"] == 9000
    assert served["reload"] is False
    assert served["log_config"] is None


def test_reload_watches_only_the_package(served: dict[str, object]) -> None:
    """`--reload` watches the package, not the working directory and its `.venv`."""
    result = runner.invoke(app, ["serve", "--reload"])

    assert result.exit_code == 0, result.output
    assert served["reload"] is True
    assert served["reload_dirs"] == [str(Path(demo_proj.__file__).parent)]


def test_serve_passes_the_env_file_on_to_the_serving_process(
    tmp_path: Path, served: dict[str, object]
) -> None:
    """The selected file reaches uvicorn, which loads it where the app is built."""
    env_file = tmp_path / "selected.env"
    env_file.write_text("LOGGING__FORMAT=json\n", encoding="utf-8")

    result = runner.invoke(app, ["serve", "--env-file", str(env_file)])

    assert result.exit_code == 0, result.output
    assert served["env_file"] == env_file


def test_serve_validates_settings_before_starting(
    tmp_path: Path, served: dict[str, object]
) -> None:
    """Invalid settings fail in `serve` itself, and uvicorn never starts."""
    env_file = tmp_path / "selected.env"
    env_file.write_text("LOGGING__FORMAT=invalid\n", encoding="utf-8")

    result = runner.invoke(app, ["serve", "--env-file", str(env_file)])

    assert result.exit_code != 0
    assert served == {}


def test_serve_rejects_a_missing_env_file(tmp_path: Path) -> None:
    """A missing path is a usage error, reported before anything loads."""
    result = runner.invoke(app, ["serve", "--env-file", str(tmp_path / "absent")])

    assert result.exit_code == 2


def test_openapi_writes_the_schema_with_lf_line_endings(tmp_path: Path) -> None:
    """`--output` creates its folder and writes LF line endings on every platform."""
    output = tmp_path / "missing" / "openapi.json"

    result = runner.invoke(app, ["openapi", "--output", str(output)])

    assert result.exit_code == 0, result.output
    content = output.read_bytes()
    assert b"\r\n" not in content
    assert "/api/health" in json.loads(content)["paths"]


def test_openapi_prints_the_schema() -> None:
    """`openapi` prints valid JSON that describes every route."""
    result = runner.invoke(app, ["openapi"])

    assert result.exit_code == 0, result.output
    assert "/api/health" in json.loads(result.stdout)["paths"]


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
