"""Template Project - A modern Python template following best practices."""

from template_project.logging import setup_logging
from template_project.settings import Settings, get_settings, reload_settings

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
    "setup_logging",
]
