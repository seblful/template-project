"""Top-level package for demo-proj."""

from importlib.metadata import PackageNotFoundError, version
from typing import Final

PROJECT_NAME: Final = "demo-proj"

try:
    __version__ = version(PROJECT_NAME)
except PackageNotFoundError:  # pragma: no cover - a source tree with no install
    __version__ = "0.0.0+unknown"

# Metadata only: re-exporting settings or logging would import pydantic and structlog
# for every importer, whether or not they are used.
__all__ = ["PROJECT_NAME", "__version__"]
