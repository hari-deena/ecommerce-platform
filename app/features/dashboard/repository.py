from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.orders.models import Order, OrderStatus
from app.features.products.models import Product
from app.features.users.models import User

LOW_STOCK_THRESHOLD = 5


class DashboardRepository:
    """Read-only cross-feature aggregation for PG-A001 (Admin Dashboard).
    Deliberately queries other features' tables directly rather than going
    through their repositories — this is a reporting exception to the usual
    feature-isolation rule, acceptable because it never writes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _scalar(self, stmt: Select) -> int:
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def total_users(self) -> int:
        return await self._scalar(select(func.count()).select_from(User))

    async def total_orders(self) -> int:
        return await self._scalar(select(func.count()).select_from(Order))

    async def total_sales(self) -> Decimal:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.PROCESSING,
                                   OrderStatus.SHIPPED, OrderStatus.DELIVERED])
            )
        )
        return Decimal(result.scalar_one())

    async def total_products(self) -> int:
        return await self._scalar(select(func.count()).select_from(Product))

    async def low_stock_products(self) -> int:
        return await self._scalar(
            select(func.count()).where(Product.stock_quantity <= LOW_STOCK_THRESHOLD)
        )

    async def pending_orders(self) -> int:
        return await self._scalar(
            select(func.count()).where(
                Order.status.in_([OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED])
            )
        )
