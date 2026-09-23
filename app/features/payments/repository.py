import uuid

from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.payments.models import Payment


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def get_for_order(self, order_id: uuid.UUID) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.order_id == order_id))
        return result.scalar_one_or_none()

    async def get_by_provider_order_id(self, provider_order_id: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.provider_order_id == provider_order_id)
        )
        return result.scalar_one_or_none()
