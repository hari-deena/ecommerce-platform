from __future__ import annotations

import uuid
from typing import Any

from app.features.audit_logs.models import AuditLog
from app.features.audit_logs.repository import AuditLogRepository


class AuditLogService:
    """Call `record(...)` from any feature service after a significant
    admin/system action (user role change, inventory adjustment, order status
    change, ...). Only `inventory.adjust_stock` is wired up as a reference —
    TODO: add calls from users/orders/coupons admin mutations as they mature."""

    def __init__(self, repository: AuditLogRepository) -> None:
        self.repository = repository

    async def record(
        self,
        *,
        actor_user_id: uuid.UUID | None,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        meta: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        return await self.repository.create(
            {
                "actor_user_id": actor_user_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "meta": meta,
                "ip_address": ip_address,
            }
        )

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[AuditLog]:
        return await self.repository.list_all(skip=skip, limit=limit)

    async def get(self, id: uuid.UUID) -> AuditLog | None:
        return await self.repository.get(id)
