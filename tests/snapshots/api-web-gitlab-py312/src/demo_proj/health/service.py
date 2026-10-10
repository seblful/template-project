"""Health check logic, free of FastAPI so it is testable without HTTP."""

from demo_proj import __version__
from demo_proj.health.schemas import Health


def get_health() -> Health:
    """Report that the service is up, and its version."""
    return Health(status="ok", version=__version__)
