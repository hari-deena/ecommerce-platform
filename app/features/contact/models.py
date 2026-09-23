from enum import StrEnum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ContactStatus(StrEnum):
    NEW = "new"
    RESPONDED = "responded"
    CLOSED = "closed"


class ContactEnquiry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """PG-006 / PG-A009 — public contact form, no authentication required."""

    __tablename__ = "contact_enquiries"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ContactStatus] = mapped_column(
        SAEnum(ContactStatus, name="contact_status"), default=ContactStatus.NEW, nullable=False
    )
