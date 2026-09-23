import uuid
from decimal import Decimal

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationAppError
from app.features.cart.schemas import AddCartItemRequest
from app.features.cart.service import CartService
from app.features.orders.models import Order, OrderStatus
from app.features.orders.repository import OrderItemRepository, OrderRepository
from app.features.orders.schemas import PlaceOrderRequest
from app.features.products.repository import ProductRepository


class OrderService:
    not_found_message = "Order not found"

    def __init__(
        self,
        repository: OrderRepository,
        item_repository: OrderItemRepository,
        product_repository: ProductRepository,
    ) -> None:
        self.repository = repository
        self.item_repository = item_repository
        self.product_repository = product_repository

    async def get_or_404(self, id: uuid.UUID) -> Order:
        order = await self.repository.get(id)
        if order is None:
            raise NotFoundError(self.not_found_message)
        return order

    async def get_owned_or_404(self, id: uuid.UUID, user_id: uuid.UUID) -> Order:
        order = await self.get_or_404(id)
        if order.user_id != user_id:
            raise ForbiddenError("This order does not belong to you")
        return order

    async def list_for_user(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 50
    ) -> list[Order]:
        return await self.repository.list_for_user(user_id, skip=skip, limit=limit)

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[Order]:
        return await self.repository.list_all(skip=skip, limit=limit)

    async def place_order(
        self, user_id: uuid.UUID, payload: PlaceOrderRequest, cart_service: CartService
    ) -> Order:
        """Creates the order as PENDING_PAYMENT without touching stock — stock is
        only decremented once `payments` confirms a successful Razorpay payment,
        so an abandoned checkout never locks inventory (FR-ORDER + FR-PAY)."""
        cart_view = await cart_service.get_view(user_id)
        if not cart_view["items"]:
            raise ValidationAppError("Cannot place an order with an empty cart")

        # TODO: shipping/tax calculation once confirmed with client (PRD §15).
        shipping_amount = Decimal(0)
        tax_amount = Decimal(0)
        subtotal = cart_view["subtotal"]
        discount_amount = cart_view["discount_amount"]
        total_amount = max(subtotal - discount_amount, Decimal(0)) + shipping_amount + tax_amount

        order = await self.repository.create(
            {
                "user_id": user_id,
                "status": OrderStatus.PENDING_PAYMENT,
                "shipping_address_id": payload.shipping_address_id,
                "coupon_code": cart_view["applied_coupon_code"],
                "subtotal": subtotal,
                "discount_amount": discount_amount,
                "shipping_amount": shipping_amount,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
            }
        )

        for item in cart_view["items"]:
            product = await self.product_repository.get(item.product_id)
            await self.item_repository.create(
                {
                    "order_id": order.id,
                    "product_id": item.product_id,
                    "product_name_snapshot": product.name if product else "Unknown product",
                    "unit_price_snapshot": item.unit_price_snapshot,
                    "quantity": item.quantity,
                    "line_total": item.unit_price_snapshot * item.quantity,
                }
            )

        await cart_service.clear(user_id)
        return await self.get_or_404(order.id)

    async def update_status(self, order: Order, new_status: OrderStatus) -> Order:
        # TODO: enforce a valid state-machine transition table once the client
        # confirms the admin order-status workflow (PRD §15).
        return await self.repository.update(order, {"status": new_status})

    async def reorder(
        self, user_id: uuid.UUID, order_id: uuid.UUID, cart_service: CartService
    ) -> dict:
        order = await self.get_owned_or_404(order_id, user_id)
        skipped: list[str] = []
        for item in order.items:
            try:
                await cart_service.add_item(
                    user_id,
                    AddCartItemRequest(product_id=item.product_id, quantity=item.quantity),
                )
            except (NotFoundError, ValidationAppError):
                skipped.append(item.product_name_snapshot)
        cart_view = await cart_service.get_view(user_id)
        return {"cart": cart_view, "skipped_items": skipped}
