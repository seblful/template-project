"""Pytest hooks for the template tests."""

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Hide this repo's venv, which `uv run pytest` exports, from generated projects.

    Otherwise every `uv run` inside a generated project warns that `VIRTUAL_ENV` does
    not match its own `.venv`. A fixture would be too late: copier's shell library
    snapshots the environment when test_template.py imports it, before any fixture.
    """
    os.environ.pop("VIRTUAL_ENV", None)
