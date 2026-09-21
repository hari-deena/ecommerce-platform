import uuid

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema
from app.features.chatbot.models import ChatRole


class ChatQueryRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None


class ChatMessageRead(IDTimestampSchema):
    session_id: uuid.UUID
    role: ChatRole
    content: str
    retrieved_product_ids: list[uuid.UUID] | None


class ChatQueryResponse(BaseModel):
    session_id: uuid.UUID
    answer: str
    retrieved_product_ids: list[uuid.UUID]
