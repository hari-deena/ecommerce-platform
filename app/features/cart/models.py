import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Cart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """FR-CART. One cart per user; the currently-applied coupon (if any) is
    snapshotted here so `orders.place_order` can price the order deterministically."""

    __tablename__ = "carts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    applied_coupon_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", name="uq_cart_item_product"),)

    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    cart: Mapped["Cart"] = relationship(back_populates="items")
