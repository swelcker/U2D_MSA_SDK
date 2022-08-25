from typing import Optional

from pydantic import BaseModel


class MSAHealthDefinition(BaseModel):
    path: str = "/healthcheck"
    interval: Optional[int] = 60
    enabled: bool = True


class MSAHealthMessage(BaseModel):
    healthy: bool = False
    message: Optional[str]
    error: Optional[str]
