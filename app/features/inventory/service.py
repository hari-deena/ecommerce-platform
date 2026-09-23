from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundError, ValidationAppError
from app.features.audit_logs.service import AuditLogService
from app.features.inventory.models import InventoryAdjustment
from app.features.inventory.repository import InventoryRepository
from app.features.inventory.schemas import InventoryAdjustmentCreate
from app.features.products.repository import ProductRepository


class InventoryService:
    """Every stock mutation goes through here so `products.stock_quantity` and
    the `inventory_adjustments` audit ledger never drift apart (FR-INV)."""

    not_found_message = "Inventory adjustment not found"

    def __init__(
        self,
        repository: InventoryRepository,
        product_repository: ProductRepository,
        audit_log_service: AuditLogService | None = None,
    ) -> None:
        self.repository = repository
        self.product_repository = product_repository
        self.audit_log_service = audit_log_service

    async def get_or_404(self, id: uuid.UUID) -> InventoryAdjustment:
        obj = await self.repository.get(id)
        if obj is None:
            raise NotFoundError(self.not_found_message)
        return obj

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[InventoryAdjustment]:
        return await self.repository.list_all(skip=skip, limit=limit)

    async def list_for_product(
        self, product_id: uuid.UUID, *, skip: int = 0, limit: int = 50
    ) -> list[InventoryAdjustment]:
        return await self.repository.list_for_product(product_id, skip=skip, limit=limit)

    async def adjust_stock(
        self, payload: InventoryAdjustmentCreate, actor_id: uuid.UUID | None
    ) -> InventoryAdjustment:
        product = await self.product_repository.get(payload.product_id)
        if product is None:
            raise NotFoundError("Product not found")

        new_stock = product.stock_quantity + payload.change_quantity
        if new_stock < 0:
            raise ValidationAppError("Adjustment would result in negative stock")

        adjustment = await self.repository.create(
            {
                "product_id": product.id,
                "change_quantity": payload.change_quantity,
                "previous_stock": product.stock_quantity,
                "new_stock": new_stock,
                "reason": payload.reason,
                "created_by": actor_id,
            }
        )
        await self.product_repository.update(product, {"stock_quantity": new_stock})

        if self.audit_log_service is not None:
            await self.audit_log_service.record(
                actor_user_id=actor_id,
                action="inventory.adjust_stock",
                entity_type="product",
                entity_id=str(product.id),
                meta={
                    "change_quantity": payload.change_quantity,
                    "previous_stock": adjustment.previous_stock,
                    "new_stock": new_stock,
                    "reason": payload.reason,
                },
            )
        return adjustment
