from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.users.repository import AddressRepository, UserRepository
from app.features.users.service import AddressService, UserService


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_address_service(db: AsyncSession = Depends(get_db)) -> AddressService:
    return AddressService(AddressRepository(db))
