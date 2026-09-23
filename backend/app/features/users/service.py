import uuid

from app.common.service import BaseService
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.core.security import hash_password
from app.features.users.models import Address, Customer, Role, User
from app.features.users.repository import (
    AddressRepository,
    CustomerRepository,
    RoleRepository,
    UserRepository,
)
from app.features.users.schemas import (
    AddressCreate,
    AddressUpdate,
    AdminUserCreate,
    AdminUserUpdate,
    UserProfileUpdate,
)


class UserService:
    """Bespoke (not generic-CRUD) service: creating/updating a user spans
    `users` and `customers` in one transaction, which the generic
    `BaseService.create/update` (single-table) can't express."""

    not_found_message = "User not found"

    def __init__(
        self,
        repository: UserRepository,
        customer_repository: CustomerRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.repository = repository
        self.customer_repository = customer_repository
        self.role_repository = role_repository

    async def get(self, id: uuid.UUID) -> User | None:
        return await self.repository.get(id)

    async def get_or_404(self, id: uuid.UUID) -> User:
        user = await self.get(id)
        if user is None:
            raise NotFoundError(self.not_found_message)
        return user

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[User]:
        return await self.repository.list_all(skip=skip, limit=limit)

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def _require_role(self, name: str) -> Role:
        role = await self.role_repository.get_by_name(name)
        if role is None:
            raise NotFoundError(f"Role '{name}' is not seeded — run migrations")
        return role

    async def create(self, payload: AdminUserCreate) -> User:
        if await self.get_by_email(payload.email):
            raise AlreadyExistsError("A user with this email already exists")

        role = await self._require_role(payload.role.value)

        user = await self.repository.create(
            {
                "email": payload.email,
                "password_hash": hash_password(payload.password),
                "role_id": role.id,
            }
        )
        await self.customer_repository.create(
            {"user_id": user.id, "full_name": payload.full_name, "phone": payload.phone}
        )
        return await self.get_or_404(user.id)

    async def update(self, user: User, payload: AdminUserUpdate) -> User:
        user_fields: dict[str, bool | int] = {}
        if payload.is_active is not None:
            user_fields["is_active"] = payload.is_active
        if payload.role is not None:
            role = await self._require_role(payload.role.value)
            user_fields["role_id"] = role.id
        if user_fields:
            await self.repository.update(user, user_fields)

        if payload.full_name is not None or payload.phone is not None:
            await self._upsert_customer_fields(
                user.id, full_name=payload.full_name, phone=payload.phone
            )

        return await self.get_or_404(user.id)

    async def delete(self, user: User) -> None:
        await self.repository.delete(user)

    async def update_profile(self, user: User, payload: UserProfileUpdate) -> User:
        await self._upsert_customer_fields(
            user.id, full_name=payload.full_name, phone=payload.phone
        )
        return await self.get_or_404(user.id)

    async def _upsert_customer_fields(
        self, user_id: uuid.UUID, *, full_name: str | None, phone: str | None
    ) -> Customer:
        customer = await self.customer_repository.get_by_user_id(user_id)
        data = {k: v for k, v in {"full_name": full_name, "phone": phone}.items() if v is not None}
        if customer is None:
            return await self.customer_repository.create(
                {"user_id": user_id, "full_name": full_name or "", "phone": phone}
            )
        return await self.customer_repository.update(customer, data)


class AddressService(BaseService[Address, AddressCreate, AddressUpdate]):
    not_found_message = "Address not found"

    def __init__(self, repository: AddressRepository) -> None:
        super().__init__(repository)
        self.repository: AddressRepository = repository

    async def list_for_user(self, user_id: uuid.UUID) -> list[Address]:
        return await self.repository.list_for_user(user_id)

    async def create_for_user(self, user_id: uuid.UUID, payload: AddressCreate) -> Address:
        return await self.repository.create({**payload.model_dump(), "user_id": user_id})
