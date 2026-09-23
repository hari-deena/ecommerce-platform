import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Product(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """FR-PROD — product catalogue entry. `stock_quantity` is the current
    denormalized count kept in sync by the `inventory` feature's adjustments;
    `inventory.InventoryAdjustment` is the audit ledger of how it got there."""

    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredients: Mapped[str | None] = mapped_column(Text, nullable=True)
    suitable_for: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # e.g. "oily skin, dry hair" — TODO: normalize to a tag table if filtering grows
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # TODO: ProductImage (one-to-many, ordered) once asset storage (S3) is decided.
