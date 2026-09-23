from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationAppError
from app.features.coupons.service import CouponService
from app.features.inventory.schemas import InventoryAdjustmentCreate
from app.features.inventory.service import InventoryService
from app.features.orders.models import OrderStatus
from app.features.orders.repository import OrderRepository
from app.features.payments.models import Payment, PaymentStatus
from app.features.payments.razorpay_client import RazorpayClient
from app.features.payments.repository import PaymentRepository
from app.features.payments.schemas import RazorpayVerifyRequest


class PaymentService:
    not_found_message = "Payment not found"

    def __init__(
        self,
        repository: PaymentRepository,
        order_repository: OrderRepository,
        inventory_service: InventoryService,
        coupon_service: CouponService,
        razorpay_client: RazorpayClient,
    ) -> None:
        self.repository = repository
        self.order_repository = order_repository
        self.inventory_service = inventory_service
        self.coupon_service = coupon_service
        self.razorpay_client = razorpay_client

    async def get_or_404(self, id: uuid.UUID) -> Payment:
        payment = await self.repository.get(id)
        if payment is None:
            raise NotFoundError(self.not_found_message)
        return payment

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[Payment]:
        return await self.repository.list_all(skip=skip, limit=limit)

    async def create_payment_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> Payment:
        order = await self.order_repository.get(order_id)
        if order is None:
            raise NotFoundError("Order not found")
        if order.user_id != user_id:
            raise ForbiddenError("This order does not belong to you")
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise ValidationAppError("This order is not awaiting payment")

        existing = await self.repository.get_for_order(order.id)
        if existing is not None and existing.status == PaymentStatus.SUCCESS:
            raise ValidationAppError("This order has already been paid for")

        razorpay_order = await self.razorpay_client.create_order(
            amount=order.total_amount, currency="INR", receipt=str(order.id)
        )

        if existing is not None:
            return await self.repository.update(
                existing,
                {"provider_order_id": razorpay_order["id"], "status": PaymentStatus.CREATED},
            )
        return await self.repository.create(
            {
                "order_id": order.id,
                "provider_order_id": razorpay_order["id"],
                "amount": order.total_amount,
                "currency": "INR",
                "status": PaymentStatus.CREATED,
            }
        )

    async def confirm_payment(self, payload: RazorpayVerifyRequest) -> Payment:
        payment = await self.repository.get_by_provider_order_id(payload.razorpay_order_id)
        if payment is None:
            raise NotFoundError("Payment not found")

        if not self.razorpay_client.verify_signature(
            razorpay_order_id=payload.razorpay_order_id,
            razorpay_payment_id=payload.razorpay_payment_id,
            razorpay_signature=payload.razorpay_signature,
        ):
            await self.repository.update(payment, {"status": PaymentStatus.FAILED})
            raise ValidationAppError("Payment signature verification failed")

        payment = await self.repository.update(
            payment,
            {
                "provider_payment_id": payload.razorpay_payment_id,
                "status": PaymentStatus.SUCCESS,
                "transaction_date": datetime.now(UTC),
            },
        )

        order = await self.order_repository.get(payment.order_id)
        if order is None:
            raise NotFoundError("Order not found")
        await self.order_repository.update(order, {"status": OrderStatus.CONFIRMED})

        # Stock is only committed once payment succeeds (see orders.service.place_order).
        for item in order.items:
            await self.inventory_service.adjust_stock(
                InventoryAdjustmentCreate(
                    product_id=item.product_id,
                    change_quantity=-item.quantity,
                    reason=f"Order {order.id} confirmed",
                ),
                actor_id=None,
            )

        if order.coupon_code:
            coupon, _ = await self.coupon_service.validate_and_price(
                order.coupon_code, order.subtotal
            )
            await self.coupon_service.record_usage(coupon)

        return payment

    async def mark_failed(self, provider_order_id: str) -> None:
        payment = await self.repository.get_by_provider_order_id(provider_order_id)
        if payment is None:
            return
        await self.repository.update(payment, {"status": PaymentStatus.FAILED})
        order = await self.order_repository.get(payment.order_id)
        if order is not None and order.status == OrderStatus.PENDING_PAYMENT:
            await self.order_repository.update(order, {"status": OrderStatus.CANCELLED})
