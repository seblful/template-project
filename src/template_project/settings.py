"""Application settings configuration using Pydantic."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings group."""

    app_name: str = Field(default="Template Project", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")


class PathsSettings(BaseSettings):
    """Path settings group."""

    base_dir: Path = Field(default_factory=lambda: Path.cwd())
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    logs_dir: Path = Field(default_factory=lambda: Path("logs"))
    models_dir: Path = Field(default_factory=lambda: Path("models"))


class LoggingSettings(BaseSettings):
    """Logging settings group."""

    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    json_output: bool = Field(default=False, description="Output JSON logs")


class Settings(BaseSettings):
    """Application settings with environment variable support using __ delimiter for nested groups."""

    app: AppSettings = Field(default_factory=AppSettings)
    paths: PathsSettings = Field(default_factory=PathsSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance, creating it if necessary."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.paths.base_dir.mkdir(parents=True, exist_ok=True)
        _settings.paths.data_dir.mkdir(parents=True, exist_ok=True)
        _settings.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        _settings.paths.models_dir.mkdir(parents=True, exist_ok=True)
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global _settings
    _settings = Settings()
    return _settings
