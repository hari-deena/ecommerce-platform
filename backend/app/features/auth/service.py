import uuid
from datetime import UTC, datetime

import jwt

from app.core.email import send_email
from app.core.exceptions import AlreadyExistsError, UnauthorizedError, ValidationAppError
from app.core.security import (
    TokenType,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.features.auth.repository import PasswordResetTokenRepository, RefreshTokenRepository
from app.features.auth.schemas import RegisterRequest, TokenResponse
from app.features.users.models import User
from app.features.users.repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        reset_repo: PasswordResetTokenRepository,
    ) -> None:
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.reset_repo = reset_repo

    async def register(self, payload: RegisterRequest) -> User:
        if await self.user_repo.get_by_email(payload.email):
            raise AlreadyExistsError("A user with this email already exists")
        user = await self.user_repo.create(
            {
                "name": payload.name,
                "email": payload.email,
                "phone": payload.phone,
                "hashed_password": hash_password(payload.password),
            }
        )
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedError("This account has been deactivated")
        return user

    async def issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id, role=user.role.value)
        refresh_token = create_refresh_token(user.id)
        payload = decode_token(refresh_token)
        await self.refresh_repo.create(
            {
                "jti": payload["jti"],
                "user_id": user.id,
                "expires_at": datetime.fromtimestamp(payload["exp"], tz=UTC),
            }
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.authenticate(email, password)
        return await self.issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired refresh token") from exc
        if payload.get("type") != TokenType.REFRESH.value:
            raise UnauthorizedError("Invalid token type")

        stored = await self.refresh_repo.get_by_jti(payload["jti"])
        if stored is None or stored.revoked_at is not None:
            raise UnauthorizedError("Refresh token has been revoked")

        user = await self.user_repo.get(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        await self.refresh_repo.revoke(stored)
        return await self.issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError:
            return
        stored = await self.refresh_repo.get_by_jti(payload.get("jti", ""))
        if stored is not None and stored.revoked_at is None:
            await self.refresh_repo.revoke(stored)

    async def forgot_password(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            # Do not leak whether the email is registered.
            return
        reset_token = create_password_reset_token(user.id)
        payload = decode_token(reset_token)
        await self.reset_repo.create(
            {
                "jti": payload["jti"],
                "user_id": user.id,
                "expires_at": datetime.fromtimestamp(payload["exp"], tz=UTC),
            }
        )
        # TODO: point at the real frontend reset-password route once confirmed.
        reset_link = f"https://app.purelioraa.com/reset-password?token={reset_token}"
        await send_email(
            to=user.email,
            subject="Reset your Pure Lioraa password",
            body=f"Click to reset your password: {reset_link}",
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        try:
            payload = decode_token(token)
        except jwt.PyJWTError as exc:
            raise ValidationAppError("Invalid or expired reset token") from exc
        if payload.get("type") != TokenType.PASSWORD_RESET.value:
            raise ValidationAppError("Invalid token type")

        stored = await self.reset_repo.get_by_jti(payload["jti"])
        if stored is None or stored.used_at is not None:
            raise ValidationAppError("This reset link has already been used")

        user = await self.user_repo.get(uuid.UUID(payload["sub"]))
        if user is None:
            raise ValidationAppError("Invalid reset token")

        await self.user_repo.update(user, {"hashed_password": hash_password(new_password)})
        await self.reset_repo.mark_used(stored)
        await self.refresh_repo.revoke_all_for_user(user.id)
