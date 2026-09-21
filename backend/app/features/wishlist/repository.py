import uuid

from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.wishlist.models import WishlistItem


class WishlistRepository(BaseRepository[WishlistItem]):
    model = WishlistItem

    async def list_for_user(self, user_id: uuid.UUID) -> list[WishlistItem]:
        result = await self.session.execute(
            select(WishlistItem).where(WishlistItem.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_for_user_and_product(
        self, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> WishlistItem | None:
        result = await self.session.execute(
            select(WishlistItem).where(
                WishlistItem.user_id == user_id, WishlistItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()
