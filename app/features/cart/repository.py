import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.core.exceptions import NotFoundError
from app.features.cart.models import Cart, CartItem


class CartRepository(BaseRepository[Cart]):
    model = Cart

    async def get_for_user(self, user_id: uuid.UUID) -> Cart | None:
        result = await self.session.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def get_or_create_for_user(self, user_id: uuid.UUID) -> Cart:
        cart = await self.get_for_user(user_id)
        if cart is not None:
            return cart

        # Re-fetch (with selectinload) rather than setting `cart.items = []` on
        # the freshly-created object — assigning to a relationship collection
        # still requires loading its current state first, which raises
        # MissingGreenlet under the async engine since nothing has awaited it.
        await self.create({"user_id": user_id})
        created = await self.get_for_user(user_id)
        if created is None:
            raise NotFoundError("Cart not found immediately after creation")
        return created


class CartItemRepository(BaseRepository[CartItem]):
    model = CartItem

    async def get_for_cart_and_product(
        self, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> CartItem | None:
        result = await self.session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id, CartItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()
