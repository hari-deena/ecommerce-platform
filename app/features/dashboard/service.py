from app.features.dashboard.repository import DashboardRepository
from app.features.dashboard.schemas import DashboardSummary


class DashboardService:
    def __init__(self, repository: DashboardRepository) -> None:
        self.repository = repository

    async def get_summary(self) -> DashboardSummary:
        return DashboardSummary(
            total_users=await self.repository.total_users(),
            total_orders=await self.repository.total_orders(),
            total_sales=await self.repository.total_sales(),
            total_products=await self.repository.total_products(),
            low_stock_products=await self.repository.low_stock_products(),
            pending_orders=await self.repository.pending_orders(),
        )

    # TODO: monthly sales/orders/revenue-trend chart series (PRD §8) once the
    # UI/UX design confirms exact granularity (daily vs monthly buckets).
