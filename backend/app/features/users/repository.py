import uuid

from sqlalchemy import select

from app.common.repository import BaseRepository
from app.features.users.models import Address, User


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()


class AddressRepository(BaseRepository[Address]):
    model = Address

    async def list_for_user(self, user_id: uuid.UUID) -> list[Address]:
        result = await self.session.execute(select(Address).where(Address.user_id == user_id))
        return list(result.scalars().all())
