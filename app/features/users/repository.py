import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.repository import BaseRepository
from app.features.users.models import Address, Customer, Role, User


class UserRepository(BaseRepository[User]):
    model = User

    _eager = (selectinload(User.role), selectinload(User.customer))

    # `populate_existing=True`: without it, re-querying a User already in this
    # session's identity map (e.g. a create-then-refetch or update-then-refetch
    # within the same request) can return stale already-loaded relationship
    # data instead of what was just written.
    async def get(self, id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == id)
            .options(*self._eager)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
            .options(*self._eager)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[User]:
        result = await self.session.execute(
            select(User)
            .options(*self._eager)
            .execution_options(populate_existing=True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    async def get_by_user_id(self, user_id: uuid.UUID) -> Customer | None:
        result = await self.session.execute(
            select(Customer).where(Customer.user_id == user_id)
        )
        return result.scalar_one_or_none()


class RoleRepository(BaseRepository[Role]):
    model = Role

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def list_all(self, *, skip: int = 0, limit: int = 50) -> list[Role]:
        result = await self.session.execute(select(Role).offset(skip).limit(limit))
        return list(result.scalars().all())


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def list_for_user(self, user_id: uuid.UUID) -> list[Address]:
        result = await self.session.execute(select(Address).where(Address.user_id == user_id))
        return list(result.scalars().all())
