import uuid

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.features.cart.schemas import AddCartItemRequest
from app.features.cart.service import CartService
from app.features.wishlist.models import WishlistItem
from app.features.wishlist.repository import WishlistRepository


class WishlistService:
    not_found_message = "Item not in wishlist"

    def __init__(self, repository: WishlistRepository) -> None:
        self.repository = repository

    async def list_for_user(self, user_id: uuid.UUID) -> list[WishlistItem]:
        return await self.repository.list_for_user(user_id)

    async def add(self, user_id: uuid.UUID, product_id: uuid.UUID) -> WishlistItem:
        if await self.repository.get_for_user_and_product(user_id, product_id):
            raise AlreadyExistsError("Product is already in your wishlist")
        return await self.repository.create({"user_id": user_id, "product_id": product_id})

    async def remove(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        item = await self.repository.get_for_user_and_product(user_id, product_id)
        if item is None:
            raise NotFoundError(self.not_found_message)
        await self.repository.delete(item)

    async def move_to_cart(
        self, user_id: uuid.UUID, product_id: uuid.UUID, cart_service: CartService
    ) -> dict:
        item = await self.repository.get_for_user_and_product(user_id, product_id)
        if item is None:
            raise NotFoundError(self.not_found_message)
        cart_view = await cart_service.add_item(
            user_id, AddCartItemRequest(product_id=product_id, quantity=1)
        )
        await self.repository.delete(item)
        return cart_view
