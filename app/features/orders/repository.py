import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.features.orders.models import Order, OrderItem


class OrderRepository(BaseRepository[Order]):
    model = Order

    async def get(self, id: uuid.UUID) -> Order | None:
        # populate_existing: `place_order` creates OrderItems via a separate
        # repo after creating the Order, then re-fetches it here in the same
        # request — see UserRepository._eager for why this matters when the
        # object is already in the session's identity map.
        result = await self.session.execute(
            select(Order)
            .where(Order.id == id)
            .options(selectinload(Order.items))
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 50
    ) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


class OrderItemRepository(BaseRepository[OrderItem]):
    model = OrderItem
