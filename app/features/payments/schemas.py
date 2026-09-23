import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.common.schemas import IDTimestampSchema
from app.features.payments.models import PaymentStatus


class CreatePaymentOrderResponse(BaseModel):
    razorpay_key_id: str
    razorpay_order_id: str
    amount: Decimal
    currency: str


class RazorpayVerifyRequest(BaseModel):
    """What the frontend Checkout.js success handler posts back to us."""

    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentRead(IDTimestampSchema):
    order_id: uuid.UUID
    provider: str
    provider_order_id: str
    provider_payment_id: str | None
    amount: Decimal
    currency: str
    status: PaymentStatus
