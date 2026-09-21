from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_admin
from app.db.session import get_db
from app.features.dashboard.repository import DashboardRepository
from app.features.dashboard.schemas import DashboardSummary
from app.features.dashboard.service import DashboardService

router = APIRouter(
    prefix="/admin/dashboard", tags=["admin:dashboard"], dependencies=[Depends(require_admin)]
)


def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    return DashboardService(DashboardRepository(db))


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummary:
    return await service.get_summary()
