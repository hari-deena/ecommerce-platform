import uuid
from enum import StrEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

# Titan Text Embeddings V2 default output dimension. Must match
# settings.BEDROCK_EMBEDDING_MODEL_ID's actual output size if that model changes.
EMBEDDING_DIM = 1024


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """FR-AI-001 / PG-009."""

    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ChatRole] = mapped_column(SAEnum(ChatRole, name="chat_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_product_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)


class KnowledgeChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """RAG corpus: product descriptions/FAQs/company content, embedded with
    Titan and stored in Postgres via pgvector — no separate vector DB needed."""

    __tablename__ = "knowledge_chunks"

    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "product" | "faq" | "company_content" — TODO: promote to enum once sources are confirmed
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
