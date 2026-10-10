"""The FastAPI application."""

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from demo_proj import PROJECT_NAME, __version__
from demo_proj.health.router import router as health_router
from demo_proj.logging import setup_logging
from demo_proj.settings import load_settings


def _operation_id(route: APIRoute) -> str:
    """Name each operation after its route function.

    A generated API client names its functions after these. FastAPI's default adds
    the path and method, so `read_health` would become `read_health_api_health_get`.
    """
    return route.name


def create_app() -> FastAPI:
    """Build the application, with every route under `/api`.

    A factory rather than a module-level app, so each test and each CLI command gets
    a fresh instance instead of sharing state through an import.
    """
    api = APIRouter(prefix="/api")
    api.include_router(health_router)
    # The interactive docs move under /api too: a frontend served from the same
    # origin owns every other path, /docs included.
    app = FastAPI(
        title=PROJECT_NAME,
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        generate_unique_id_function=_operation_id,
    )
    app.include_router(api)
    return app


def create_serving_app() -> FastAPI:
    """Configure logging from the environment, then build the application.

    This is what uvicorn calls, in the process that serves. With reload that is a
    fresh child process, which inherits the environment but neither the parent's
    arguments nor its logging setup, so both are redone here.
    """
    setup_logging(load_settings().logging)
    return create_app()
