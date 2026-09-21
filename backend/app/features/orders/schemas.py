import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema
from app.features.orders.models import OrderStatus


class PlaceOrderRequest(BaseModel):
    shipping_address_id: uuid.UUID


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemRead(IDTimestampSchema):
    product_id: uuid.UUID
    product_name_snapshot: str
    unit_price_snapshot: Decimal
    quantity: int
    line_total: Decimal


class OrderRead(IDTimestampSchema):
    user_id: uuid.UUID
    status: OrderStatus
    shipping_address_id: uuid.UUID | None
    coupon_code: str | None
    subtotal: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    items: list[OrderItemRead]
