import uuid
from collections.abc import Callable, Sequence
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.v1.deps import require_admin
from app.common.service import BaseService
from app.core.exceptions import NotFoundError


def build_crud_router(
    *,
    service_dependency: Callable[..., Any],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    prefix: str,
    tags: Sequence[str],
    require_admin_read: bool = False,
    require_admin_write: bool = True,
) -> APIRouter:
    """Wires standard list/get/create/update/delete endpoints for a feature.

    Read routes are public unless `require_admin_read=True` (e.g. coupons,
    inventory adjustments, audit-adjacent data an anonymous customer should
    never see). Write routes require an admin by default, matching every
    catalog-style admin capability in the PRD (Products, Categories, News,
    Coupons, Inventory).
    """
    router = APIRouter(prefix=prefix, tags=list(tags))
    read_deps = [Depends(require_admin)] if require_admin_read else []
    write_deps = [Depends(require_admin)] if require_admin_write else []

    @router.get("/", response_model=list[read_schema], dependencies=read_deps)  # type: ignore[valid-type]
    async def list_items(
        skip: int = 0, limit: int = 50, service: BaseService = Depends(service_dependency)
    ) -> list[Any]:
        return await service.list_all(skip=skip, limit=limit)

    @router.get("/{item_id}", response_model=read_schema, dependencies=read_deps)
    async def get_item(
        item_id: uuid.UUID, service: BaseService = Depends(service_dependency)
    ) -> Any:
        return await service.get_or_404(item_id)

    @router.post(
        "/",
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        dependencies=write_deps,
    )
    async def create_item(
        payload: create_schema, service: BaseService = Depends(service_dependency)  # type: ignore[valid-type]
    ) -> Any:
        return await service.create(payload)

    @router.patch("/{item_id}", response_model=read_schema, dependencies=write_deps)
    async def update_item(
        item_id: uuid.UUID,
        payload: update_schema,  # type: ignore[valid-type]
        service: BaseService = Depends(service_dependency),
    ) -> Any:
        obj = await service.get(item_id)
        if obj is None:
            raise NotFoundError(service.not_found_message)
        return await service.update(obj, payload)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=write_deps)
    async def delete_item(
        item_id: uuid.UUID, service: BaseService = Depends(service_dependency)
    ) -> None:
        obj = await service.get_or_404(item_id)
        await service.delete(obj)

    return router
