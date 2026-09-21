import uuid
from decimal import Decimal

from app.core.exceptions import NotFoundError, ValidationAppError
from app.features.cart.models import Cart
from app.features.cart.repository import CartItemRepository, CartRepository
from app.features.cart.schemas import AddCartItemRequest
from app.features.coupons.service import CouponService
from app.features.products.repository import ProductRepository


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository,
        item_repo: CartItemRepository,
        product_repo: ProductRepository,
        coupon_service: CouponService,
    ) -> None:
        self.cart_repo = cart_repo
        self.item_repo = item_repo
        self.product_repo = product_repo
        self.coupon_service = coupon_service

    @staticmethod
    def subtotal(cart: Cart) -> Decimal:
        return sum((item.unit_price_snapshot * item.quantity for item in cart.items), Decimal(0))

    async def get_view(self, user_id: uuid.UUID) -> dict:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        subtotal = self.subtotal(cart)
        return {
            "id": cart.id,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
            "user_id": cart.user_id,
            "applied_coupon_code": cart.applied_coupon_code,
            "discount_amount": cart.discount_amount,
            "items": cart.items,
            "subtotal": subtotal,
            "total": max(subtotal - cart.discount_amount, Decimal(0)),
        }

    async def _revalidate_coupon(self, cart: Cart) -> None:
        """Re-checks the applied coupon after the cart contents change (min
        purchase amount may no longer be met). Silently drops an invalid coupon
        rather than blocking the cart mutation."""
        if cart.applied_coupon_code is None:
            return
        try:
            _, discount = await self.coupon_service.validate_and_price(
                cart.applied_coupon_code, self.subtotal(cart)
            )
            await self.cart_repo.update(cart, {"discount_amount": discount})
        except ValidationAppError:
            await self.cart_repo.update(
                cart, {"applied_coupon_code": None, "discount_amount": Decimal(0)}
            )

    async def add_item(self, user_id: uuid.UUID, payload: AddCartItemRequest) -> dict:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        product = await self.product_repo.get(payload.product_id)
        if product is None or not product.is_active:
            raise NotFoundError("Product not found")

        existing = await self.item_repo.get_for_cart_and_product(cart.id, product.id)
        requested_total = payload.quantity + (existing.quantity if existing else 0)
        if requested_total > product.stock_quantity:
            raise ValidationAppError("Requested quantity exceeds available stock")

        unit_price = product.discount_price or product.price
        if existing:
            await self.item_repo.update(
                existing, {"quantity": requested_total, "unit_price_snapshot": unit_price}
            )
        else:
            await self.item_repo.create(
                {
                    "cart_id": cart.id,
                    "product_id": product.id,
                    "quantity": payload.quantity,
                    "unit_price_snapshot": unit_price,
                }
            )

        refreshed_cart = await self.cart_repo.get_for_user(user_id)
        if refreshed_cart is None:
            raise NotFoundError("Cart not found")
        await self._revalidate_coupon(refreshed_cart)
        return await self.get_view(user_id)

    async def update_item_quantity(
        self, user_id: uuid.UUID, product_id: uuid.UUID, quantity: int
    ) -> dict:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        item = await self.item_repo.get_for_cart_and_product(cart.id, product_id)
        if item is None:
            raise NotFoundError("Item not in cart")

        product = await self.product_repo.get(product_id)
        if product is None or quantity > product.stock_quantity:
            raise ValidationAppError("Requested quantity exceeds available stock")

        await self.item_repo.update(item, {"quantity": quantity})
        refreshed_cart = await self.cart_repo.get_for_user(user_id)
        if refreshed_cart is None:
            raise NotFoundError("Cart not found")
        await self._revalidate_coupon(refreshed_cart)
        return await self.get_view(user_id)

    async def remove_item(self, user_id: uuid.UUID, product_id: uuid.UUID) -> dict:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        item = await self.item_repo.get_for_cart_and_product(cart.id, product_id)
        if item is None:
            raise NotFoundError("Item not in cart")
        await self.item_repo.delete(item)
        refreshed_cart = await self.cart_repo.get_for_user(user_id)
        if refreshed_cart is None:
            raise NotFoundError("Cart not found")
        await self._revalidate_coupon(refreshed_cart)
        return await self.get_view(user_id)

    async def clear(self, user_id: uuid.UUID) -> None:
        cart = await self.cart_repo.get_for_user(user_id)
        if cart is None:
            return
        for item in list(cart.items):
            await self.item_repo.delete(item)
        await self.cart_repo.update(
            cart, {"applied_coupon_code": None, "discount_amount": Decimal(0)}
        )

    async def apply_coupon(self, user_id: uuid.UUID, code: str) -> dict:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        _, discount = await self.coupon_service.validate_and_price(code, self.subtotal(cart))
        await self.cart_repo.update(
            cart, {"applied_coupon_code": code.upper(), "discount_amount": discount}
        )
        return await self.get_view(user_id)

    async def remove_coupon(self, user_id: uuid.UUID) -> dict:
        cart = await self.cart_repo.get_or_create_for_user(user_id)
        await self.cart_repo.update(
            cart, {"applied_coupon_code": None, "discount_amount": Decimal(0)}
        )
        return await self.get_view(user_id)
