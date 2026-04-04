"""Configuration package - re-exports from template_project for backward compatibility."""

from template_project.logging import setup_logging
from template_project.settings import Settings, get_settings, reload_settings

__all__ = [
    "setup_logging",
    "Settings",
    "get_settings",
    "reload_settings",
]
