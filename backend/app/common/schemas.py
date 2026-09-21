import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMBaseSchema(BaseModel):
    """Base for read schemas that map directly from SQLAlchemy models."""

    model_config = ConfigDict(from_attributes=True)


class IDTimestampSchema(ORMBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PageParams(BaseModel):
    skip: int = 0
    limit: int = 50


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
