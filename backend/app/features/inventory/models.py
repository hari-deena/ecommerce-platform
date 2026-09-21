import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class InventoryAdjustment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """FR-INV — append-only audit ledger of stock changes (PG-A005). Never
    updated or deleted; the current count lives denormalized on `Product.stock_quantity`."""

    __tablename__ = "inventory_adjustments"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    change_quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # signed delta
    previous_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    new_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
