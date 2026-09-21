import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.features.cart.models import Cart, CartItem


class CartRepository(BaseRepository[Cart]):
    model = Cart

    async def get_for_user(self, user_id: uuid.UUID) -> Cart | None:
        result = await self.session.execute(
            select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items))
        )
        return result.scalar_one_or_none()

    async def get_or_create_for_user(self, user_id: uuid.UUID) -> Cart:
        cart = await self.get_for_user(user_id)
        if cart is None:
            cart = await self.create({"user_id": user_id})
            cart.items = []
        return cart


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
