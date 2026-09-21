import uuid

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema


class WishlistItemCreate(BaseModel):
    product_id: uuid.UUID


class WishlistItemRead(IDTimestampSchema):
    user_id: uuid.UUID
    product_id: uuid.UUID
