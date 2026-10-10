"""HTTP routes of the health check: status codes and paths, no logic."""

from fastapi import APIRouter

from demo_proj.health.schemas import Health
from demo_proj.health.service import get_health

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def read_health() -> Health:
    """Return the service's health."""
    return get_health()
