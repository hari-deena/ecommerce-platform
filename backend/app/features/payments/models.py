import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PaymentStatus(StrEnum):
    CREATED = "created"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """FR-PAY — Razorpay integration."""

    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"), unique=True, nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(30), default="razorpay", nullable=False)
    provider_order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.CREATED,
        nullable=False,
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    transaction_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
