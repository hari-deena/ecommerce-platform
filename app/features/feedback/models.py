import uuid
from enum import StrEnum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class FeedbackStatus(StrEnum):
    NEW = "new"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class Feedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """PG-A008 — customer feedback."""

    __tablename__ = "feedback"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[FeedbackStatus] = mapped_column(
        SAEnum(FeedbackStatus, name="feedback_status"), default=FeedbackStatus.NEW, nullable=False
    )
