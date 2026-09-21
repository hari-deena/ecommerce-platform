import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.common.schemas import IDTimestampSchema


class AddCartItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(ge=1)


class ApplyCouponRequest(BaseModel):
    code: str


class CartItemRead(IDTimestampSchema):
    product_id: uuid.UUID
    quantity: int
    unit_price_snapshot: Decimal

    @property
    def line_total(self) -> Decimal:
        return self.unit_price_snapshot * self.quantity


class CartRead(IDTimestampSchema):
    user_id: uuid.UUID
    applied_coupon_code: str | None
    discount_amount: Decimal
    items: list[CartItemRead]
    subtotal: Decimal
    total: Decimal
