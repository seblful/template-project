"""Template Project - A modern Python template following best practices."""

from config import get_settings, Settings, reload_settings
from config import get_logger, setup_logging, LoggerMixin, log_exception

__version__ = "0.1.0"
__author__ = "seblful"
__email__ = "alesha.chimba@gmail.com"

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "get_settings",
    "Settings",
    "reload_settings",
    "get_logger",
    "setup_logging",
    "LoggerMixin",
    "log_exception",
]

logger = get_logger(__name__)
