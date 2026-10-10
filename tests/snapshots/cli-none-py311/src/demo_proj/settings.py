"""Application settings, loaded and validated with pydantic-settings."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LoggingSettings(BaseModel):
    """Logging settings group."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["text", "json"] = Field(
        default="text", description="Console log format"
    )
    level: LogLevel = Field(default="INFO", description="Lowest level that is logged")

    @field_validator("level", mode="before")
    @classmethod
    def _upper_case_level(cls, value: object) -> object:
        """Accept the level in any letter case, as in `LEVEL=info`."""
        return value.upper() if isinstance(value, str) else value


class Settings(BaseSettings):
    """Application settings, read from variables prefixed `DEMO_PROJ_`.

    Groups are `__`-delimited, as in `DEMO_PROJ_LOGGING__LEVEL`.

    Constructor arguments win over environment variables, which win over defaults. No
    dotenv file is read: `uv run --env-file .env` loads one into the environment.
    """

    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    model_config = SettingsConfigDict(
        # Keeps generic names the platform sets, such as HOST or PORT, from colliding.
        env_prefix="DEMO_PROJ_",
        env_nested_delimiter="__",
        frozen=True,
    )
