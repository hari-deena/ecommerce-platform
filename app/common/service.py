from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.common.repository import BaseRepository, ModelType
from app.core.exceptions import NotFoundError

CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchema, UpdateSchema]):
    """Generic business-logic layer sitting between routers and repositories.

    Stub features use this as-is for plain CRUD; features with real business
    rules (stock checks, coupon math, ownership scoping) override the relevant
    methods instead of calling `super()`.
    """

    not_found_message = "Resource not found"

    def __init__(self, repository: BaseRepository[ModelType]) -> None:
        self.repository = repository

    async def get(self, id: uuid.UUID) -> ModelType | None:
        return await self.repository.get(id)

    async def get_or_404(self, id: uuid.UUID) -> ModelType:
        obj = await self.get(id)
        if obj is None:
            raise NotFoundError(self.not_found_message)
        return obj

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[ModelType]:
        return await self.repository.list_all(skip=skip, limit=limit)

    async def create(self, payload: CreateSchema) -> ModelType:
        return await self.repository.create(payload.model_dump())

    async def update(self, obj: ModelType, payload: UpdateSchema) -> ModelType:
        return await self.repository.update(obj, payload.model_dump(exclude_unset=True))

    async def delete(self, obj: ModelType) -> None:
        await self.repository.delete(obj)
