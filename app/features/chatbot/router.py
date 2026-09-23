import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_optional_user
from app.db.session import get_db
from app.features.chatbot.bedrock_client import BedrockClient
from app.features.chatbot.models import ChatMessage
from app.features.chatbot.repository import (
    ChatMessageRepository,
    ChatSessionRepository,
    KnowledgeChunkRepository,
)
from app.features.chatbot.schemas import ChatMessageRead, ChatQueryRequest, ChatQueryResponse
from app.features.chatbot.service import ChatbotService
from app.features.users.models import User

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


def get_chatbot_service(db: AsyncSession = Depends(get_db)) -> ChatbotService:
    return ChatbotService(
        ChatSessionRepository(db),
        ChatMessageRepository(db),
        KnowledgeChunkRepository(db),
        BedrockClient(),
    )


@router.post("/query", response_model=ChatQueryResponse)
async def ask_chatbot(
    payload: ChatQueryRequest,
    user: User | None = Depends(get_optional_user),
    service: ChatbotService = Depends(get_chatbot_service),
) -> ChatQueryResponse:
    """PG-009 — usable by guests and logged-in customers alike."""
    return await service.ask(
        message=payload.message,
        session_id=payload.session_id,
        user_id=user.id if user else None,
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
async def get_session_messages(
    session_id: uuid.UUID,
    user: User | None = Depends(get_optional_user),
    service: ChatbotService = Depends(get_chatbot_service),
) -> list[ChatMessage]:
    return await service.get_session_messages(session_id, user.id if user else None)
