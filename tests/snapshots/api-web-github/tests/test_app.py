"""Tests for building the application."""

import json

import pytest
from fastapi import FastAPI

from demo_proj.app import create_app, create_serving_app
from demo_proj.logging import get_logger


def test_operations_are_named_after_their_route_functions() -> None:
    """A generated client gets `read_health`, not `read_health_api_health_get`."""
    operation = create_app().openapi()["paths"]["/api/health"]["get"]

    assert operation["operationId"] == "read_health"


def test_serving_app_configures_logging_from_the_environment(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The app uvicorn builds logs in the format the environment selects."""
    monkeypatch.setenv("LOGGING__FORMAT", "json")

    assert isinstance(create_serving_app(), FastAPI)

    get_logger("test").info("serving")
    assert json.loads(capsys.readouterr().err)["event"] == "serving"
