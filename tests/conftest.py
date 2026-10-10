"""Pytest setup for the template tests."""

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
# The one file whose floors decide what uv resolves in a generated project.
DEPENDENCIES = "template/pyproject.toml.jinja"


def _dependencies_last_changed() -> str | None:
    """Return when the generated projects' Python dependencies last changed, or None.

    Every project resolves its dependencies fresh, so without a cutoff any upstream
    release can fail an unrelated change. Resolving as of the commit that last touched
    the floors fixes that without a date to maintain: a floor cannot be newer than the
    commit that added it, so resolution never fails, and an upstream release after it
    stays out until the floors change again. Uncommitted changes count as now, and the
    weekly canary run sets TEMPLATE_UNPINNED to resolve the newest releases anyway, so
    breakage still surfaces. Bun has no such cutoff: the web app's caret ranges resolve
    fresh either way.

    Needs the full history: a shallow clone reports its tip commit, whatever changed.
    """

    def git(*args: str) -> str:
        """Return git's output, or nothing when git is missing or fails."""
        try:
            result = subprocess.run(
                ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
            )
        except OSError:
            return ""
        return result.stdout.strip() if result.returncode == 0 else ""

    if git("status", "--porcelain", "--", DEPENDENCIES):
        return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return git("log", "-1", "--format=%cI", "--", DEPENDENCIES) or None


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the flag that rewrites the committed snapshots."""
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        help="rewrite tests/snapshots from what the template renders now",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Pin dependency resolution and hide this repo's venv from generated projects.

    `uv run pytest` exports `VIRTUAL_ENV`, so every `uv run` inside a generated
    project would warn that it does not match the project's own `.venv`. A fixture
    would be too late: copier's shell library snapshots the environment when the test
    modules import it, before any fixture.
    """
    os.environ.pop("VIRTUAL_ENV", None)
    if os.environ.get("TEMPLATE_UNPINNED"):
        return
    if cutoff := _dependencies_last_changed():
        os.environ.setdefault("UV_EXCLUDE_NEWER", cutoff)
