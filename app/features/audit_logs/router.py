import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_admin
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.features.audit_logs.models import AuditLog
from app.features.audit_logs.repository import AuditLogRepository
from app.features.audit_logs.schemas import AuditLogRead
from app.features.audit_logs.service import AuditLogService

router = APIRouter(
    prefix="/admin/audit-logs", tags=["admin:audit-logs"], dependencies=[Depends(require_admin)]
)


def get_audit_log_service(db: AsyncSession = Depends(get_db)) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))


@router.get("/", response_model=list[AuditLogRead])
async def list_audit_logs(
    skip: int = 0, limit: int = 50, service: AuditLogService = Depends(get_audit_log_service)
) -> list[AuditLog]:
    return await service.list_all(skip=skip, limit=limit)


@router.get("/{log_id}", response_model=AuditLogRead)
async def get_audit_log(
    log_id: uuid.UUID, service: AuditLogService = Depends(get_audit_log_service)
) -> AuditLog:
    log = await service.get(log_id)
    if log is None:
        raise NotFoundError("Audit log not found")
    return log
