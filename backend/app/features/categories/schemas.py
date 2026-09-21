import uuid

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    parent_id: uuid.UUID | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    parent_id: uuid.UUID | None = None
    is_active: bool | None = None


class CategoryRead(IDTimestampSchema):
    name: str
    slug: str
    description: str | None
    parent_id: uuid.UUID | None
    is_active: bool
