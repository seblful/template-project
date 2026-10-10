"""Response models of the health check, and so part of the API contract."""

from typing import Literal

from pydantic import BaseModel


class Health(BaseModel):
    """Whether the service is up, and which version is running."""

    status: Literal["ok"]
    version: str
