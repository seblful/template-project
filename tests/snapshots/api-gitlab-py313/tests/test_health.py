"""Tests for the health check."""

from fastapi.testclient import TestClient

from demo_proj import __version__
from demo_proj.app import create_app


def test_health_endpoint_reports_the_running_version() -> None:
    """`GET /api/health` answers 200 with the installed version."""
    response = TestClient(create_app()).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
