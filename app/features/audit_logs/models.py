import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """PG-A012 — append-only. Written only via `AuditLogService.record(...)` from
    other features' services; never exposed through a public create/update/delete route."""

    __tablename__ = "audit_logs"

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
