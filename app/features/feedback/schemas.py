import uuid

from pydantic import BaseModel, Field

from app.common.schemas import IDTimestampSchema
from app.features.feedback.models import FeedbackStatus


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    message: str


class FeedbackStatusUpdate(BaseModel):
    status: FeedbackStatus


class FeedbackRead(IDTimestampSchema):
    user_id: uuid.UUID | None
    rating: int
    message: str
    status: FeedbackStatus
