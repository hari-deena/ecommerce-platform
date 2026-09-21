from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.auth.repository import PasswordResetTokenRepository, RefreshTokenRepository
from app.features.auth.service import AuthService
from app.features.users.repository import UserRepository


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=UserRepository(db),
        refresh_repo=RefreshTokenRepository(db),
        reset_repo=PasswordResetTokenRepository(db),
    )
