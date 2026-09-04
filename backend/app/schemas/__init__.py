"""
Pydantic v2 schemas package for request validation and response serialization.
"""
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok", json_schema_extra={"example": "ok"})
    service: str = Field(default="recoverai-api", json_schema_extra={"example": "recoverai-api"})
    version: str = Field(default="0.1.0", json_schema_extra={"example": "0.1.0"})


class DetailedHealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: dict
    redis: dict
