import uuid

from app.core.exceptions import ForbiddenError, NotFoundError
from app.features.chatbot.bedrock_client import BedrockClient
from app.features.chatbot.models import ChatMessage, ChatRole, ChatSession
from app.features.chatbot.repository import (
    ChatMessageRepository,
    ChatSessionRepository,
    KnowledgeChunkRepository,
)
from app.features.chatbot.schemas import ChatQueryResponse


class ChatbotService:
    def __init__(
        self,
        session_repo: ChatSessionRepository,
        message_repo: ChatMessageRepository,
        chunk_repo: KnowledgeChunkRepository,
        bedrock: BedrockClient,
    ) -> None:
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.chunk_repo = chunk_repo
        self.bedrock = bedrock

    async def _get_or_create_session(
        self, session_id: uuid.UUID | None, user_id: uuid.UUID | None
    ) -> ChatSession:
        if session_id is None:
            return await self.session_repo.create({"user_id": user_id})
        session = await self.session_repo.get(session_id)
        if session is None:
            raise NotFoundError("Chat session not found")
        if user_id is not None and session.user_id not in (None, user_id):
            raise ForbiddenError("This chat session does not belong to you")
        return session

    async def ask(
        self, *, message: str, session_id: uuid.UUID | None, user_id: uuid.UUID | None
    ) -> ChatQueryResponse:
        session = await self._get_or_create_session(session_id, user_id)
        await self.message_repo.create(
            {"session_id": session.id, "role": ChatRole.USER, "content": message}
        )

        query_embedding = await self.bedrock.embed_text(message)
        chunks = await self.chunk_repo.similarity_search(query_embedding, top_k=5)

        answer = await self.bedrock.generate_answer(
            question=message, context_chunks=[c.content for c in chunks]
        )
        retrieved_product_ids = list({c.product_id for c in chunks if c.product_id is not None})

        await self.message_repo.create(
            {
                "session_id": session.id,
                "role": ChatRole.ASSISTANT,
                "content": answer,
                "retrieved_product_ids": [str(pid) for pid in retrieved_product_ids],
            }
        )

        return ChatQueryResponse(
            session_id=session.id, answer=answer, retrieved_product_ids=retrieved_product_ids
        )

    async def get_session_messages(
        self, session_id: uuid.UUID, user_id: uuid.UUID | None
    ) -> list[ChatMessage]:
        session = await self.session_repo.get(session_id)
        if session is None:
            raise NotFoundError("Chat session not found")
        if user_id is not None and session.user_id not in (None, user_id):
            raise ForbiddenError("This chat session does not belong to you")
        return await self.message_repo.list_for_session(session_id)
