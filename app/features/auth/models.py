import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks issued refresh tokens by JWT id (`jti`) so they can be revoked
    (logout, password change, admin-forced sign-out) instead of only relying
    on client-side expiry — required for FR-AUTH-002 secure login."""

    __tablename__ = "refresh_tokens"

    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PasswordResetToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Supports FR-AUTH-003 (password recovery through email)."""

    __tablename__ = "password_reset_tokens"

    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
