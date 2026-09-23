import uuid

from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.chatbot.models import ChatMessage, ChatSession, KnowledgeChunk


class ChatSessionRepository(BaseRepository[ChatSession]):
    model = ChatSession


class ChatMessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage

    async def list_for_session(self, session_id: uuid.UUID) -> list[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())


class KnowledgeChunkRepository(BaseRepository[KnowledgeChunk]):
    model = KnowledgeChunk

    async def similarity_search(
        self, query_embedding: list[float], *, top_k: int = 5
    ) -> list[KnowledgeChunk]:
        """Cosine-distance nearest-neighbour search via pgvector. Requires an
        ivfflat/hnsw index on `embedding` in production for performant recall
        at scale — see the initial Alembic migration."""
        result = await self.session.execute(
            select(KnowledgeChunk)
            .order_by(KnowledgeChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return list(result.scalars().all())
