import uuid

from app.common.service import BaseService
from app.core.exceptions import AlreadyExistsError
from app.core.security import hash_password
from app.features.users.models import Address, User
from app.features.users.repository import AddressRepository, UserRepository
from app.features.users.schemas import (
    AddressCreate,
    AddressUpdate,
    AdminUserCreate,
    AdminUserUpdate,
    UserProfileUpdate,
)


class UserService(BaseService[User, AdminUserCreate, AdminUserUpdate]):
    not_found_message = "User not found"

    def __init__(self, repository: UserRepository) -> None:
        super().__init__(repository)
        self.repository: UserRepository = repository

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def create(self, payload: AdminUserCreate) -> User:
        if await self.get_by_email(payload.email):
            raise AlreadyExistsError("A user with this email already exists")
        data = payload.model_dump()
        raw_password = data.pop("password")
        data["hashed_password"] = hash_password(raw_password)
        return await self.repository.create(data)

    async def update_profile(self, user: User, payload: UserProfileUpdate) -> User:
        """Self-service profile update — distinct from `update()` (which is typed
        for the admin CRUD schema) since customers can't set role/is_active."""
        return await self.repository.update(user, payload.model_dump(exclude_unset=True))


class AddressService(BaseService[Address, AddressCreate, AddressUpdate]):
    not_found_message = "Address not found"

    def __init__(self, repository: AddressRepository) -> None:
        super().__init__(repository)
        self.repository: AddressRepository = repository

    async def list_for_user(self, user_id: uuid.UUID) -> list[Address]:
        return await self.repository.list_for_user(user_id)

    async def create_for_user(self, user_id: uuid.UUID, payload: AddressCreate) -> Address:
        return await self.repository.create({**payload.model_dump(), "user_id": user_id})
