import uuid
from datetime import datetime

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema


class NewsArticleCreate(BaseModel):
    title: str
    slug: str
    content: str
    cover_image_url: str | None = None
    is_published: bool = False
    published_at: datetime | None = None


class NewsArticleUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    is_published: bool | None = None
    published_at: datetime | None = None


class NewsArticleRead(IDTimestampSchema):
    title: str
    slug: str
    content: str
    cover_image_url: str | None
    is_published: bool
    published_at: datetime | None
    author_id: uuid.UUID | None
