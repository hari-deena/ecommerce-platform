import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_admin
from app.db.session import get_db
from app.features.audit_logs.repository import AuditLogRepository
from app.features.audit_logs.service import AuditLogService
from app.features.inventory.models import InventoryAdjustment
from app.features.inventory.repository import InventoryRepository
from app.features.inventory.schemas import InventoryAdjustmentCreate, InventoryAdjustmentRead
from app.features.inventory.service import InventoryService
from app.features.products.repository import ProductRepository
from app.features.users.models import User

router = APIRouter(
    prefix="/admin/inventory", tags=["admin:inventory"], dependencies=[Depends(require_admin)]
)


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    return InventoryService(
        InventoryRepository(db),
        ProductRepository(db),
        AuditLogService(AuditLogRepository(db)),
    )


@router.get("/", response_model=list[InventoryAdjustmentRead])
async def list_adjustments(
    skip: int = 0, limit: int = 50, service: InventoryService = Depends(get_inventory_service)
) -> list[InventoryAdjustment]:
    return await service.list_all(skip=skip, limit=limit)


@router.get("/product/{product_id}", response_model=list[InventoryAdjustmentRead])
async def list_adjustments_for_product(
    product_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryAdjustment]:
    return await service.list_for_product(product_id, skip=skip, limit=limit)


@router.post("/", response_model=InventoryAdjustmentRead, status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    payload: InventoryAdjustmentCreate,
    admin: User = Depends(require_admin),
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryAdjustment:
    return await service.adjust_stock(payload, actor_id=admin.id)
