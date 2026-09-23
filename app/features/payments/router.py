import uuid

import structlog
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, require_admin
from app.core.exceptions import ValidationAppError
from app.db.session import get_db
from app.features.coupons.repository import CouponRepository
from app.features.coupons.service import CouponService
from app.features.inventory.repository import InventoryRepository
from app.features.inventory.service import InventoryService
from app.features.orders.repository import OrderRepository
from app.features.payments.models import Payment
from app.features.payments.razorpay_client import RazorpayClient
from app.features.payments.repository import PaymentRepository
from app.features.payments.schemas import (
    CreatePaymentOrderResponse,
    PaymentRead,
    RazorpayVerifyRequest,
)
from app.features.payments.service import PaymentService
from app.features.products.repository import ProductRepository
from app.features.users.models import User

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(
        PaymentRepository(db),
        OrderRepository(db),
        InventoryService(InventoryRepository(db), ProductRepository(db)),
        CouponService(CouponRepository(db)),
        RazorpayClient(),
    )


@router.post("/orders/{order_id}/razorpay-order", response_model=CreatePaymentOrderResponse)
async def create_razorpay_order(
    order_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: PaymentService = Depends(get_payment_service),
) -> CreatePaymentOrderResponse:
    from app.core.config import settings

    payment = await service.create_payment_order(order_id, user.id)
    return CreatePaymentOrderResponse(
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
        razorpay_order_id=payment.provider_order_id,
        amount=payment.amount,
        currency=payment.currency,
    )


@router.post("/verify", response_model=PaymentRead)
async def verify_payment(
    payload: RazorpayVerifyRequest,
    user: User = Depends(get_current_active_user),
    service: PaymentService = Depends(get_payment_service),
) -> Payment:
    """Called by the frontend's Checkout.js success handler. `/payments/webhook`
    below is the source of truth for server-to-server confirmation; this route
    lets the UI reflect success immediately without waiting on the webhook."""
    return await service.confirm_payment(payload)


@router.post("/webhook", status_code=status.HTTP_200_OK, include_in_schema=False)
async def razorpay_webhook(
    request: Request, service: PaymentService = Depends(get_payment_service)
) -> dict[str, str]:
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not RazorpayClient().verify_webhook_signature(body=body, signature=signature):
        raise ValidationAppError("Invalid webhook signature")

    event = await request.json()
    event_type = event.get("event", "")
    payload = event.get("payload", {}).get("payment", {}).get("entity", {})

    if event_type == "payment.captured":
        await service.confirm_payment(
            RazorpayVerifyRequest(
                razorpay_order_id=payload.get("order_id", ""),
                razorpay_payment_id=payload.get("id", ""),
                razorpay_signature=signature,
            )
        )
    elif event_type == "payment.failed":
        await service.mark_failed(payload.get("order_id", ""))
    else:
        logger.info("razorpay_webhook_ignored", event_type=event_type)

    return {"status": "ok"}


admin_router = APIRouter(
    prefix="/admin/payments", tags=["admin:payments"], dependencies=[Depends(require_admin)]
)


@admin_router.get("/", response_model=list[PaymentRead])
async def list_payments(
    skip: int = 0, limit: int = 50, service: PaymentService = Depends(get_payment_service)
) -> list[Payment]:
    return await service.list_all(skip=skip, limit=limit)


@admin_router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: uuid.UUID, service: PaymentService = Depends(get_payment_service)
) -> Payment:
    return await service.get_or_404(payment_id)


# NOTE: exported separately, not nested under `router` — see users/router.py note.
