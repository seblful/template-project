"""Pytest setup for the template tests."""

import os

import pytest

# The newest dependency release a generated project may resolve to. Every project
# resolves its dependencies fresh, so without a date any upstream release can fail an
# unrelated change. Move it forward on purpose, and never before the newest floor in
# pyproject.toml.jinja, or resolution fails. The weekly canary run sets
# TEMPLATE_UNPINNED and resolves current releases, so breakage still surfaces. Bun has
# no such cutoff: the web app's caret ranges resolve fresh either way.
PINNED_DATE = "2026-10-10T00:00:00Z"


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
    if not os.environ.get("TEMPLATE_UNPINNED"):
        os.environ.setdefault("UV_EXCLUDE_NEWER", PINNED_DATE)
