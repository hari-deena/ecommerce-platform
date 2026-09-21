import uuid

from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.inventory.models import InventoryAdjustment


class InventoryRepository(BaseRepository[InventoryAdjustment]):
    model = InventoryAdjustment

    async def list_for_product(
        self, product_id: uuid.UUID, *, skip: int = 0, limit: int = 50
    ) -> list[InventoryAdjustment]:
        result = await self.session.execute(
            select(InventoryAdjustment)
            .where(InventoryAdjustment.product_id == product_id)
            .order_by(InventoryAdjustment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
