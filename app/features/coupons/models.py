from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DiscountType(StrEnum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Coupon(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """FR-COUP — e.g. BEAUTY20: 20% off, dated, with min purchase / max discount caps."""

    __tablename__ = "coupons"

    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    discount_type: Mapped[DiscountType] = mapped_column(
        SAEnum(DiscountType, name="discount_type"), nullable=False
    )
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    min_purchase_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
