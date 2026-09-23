import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


def hash_password(raw_password: str) -> str:
    return _hasher.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return _hasher.verify(hashed_password, raw_password)
    except VerifyMismatchError:
        return False


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta, **extra_claims: Any) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
        **extra_claims,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    return _create_token(
        str(user_id),
        TokenType.ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        role=role,
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    return _create_token(
        str(user_id),
        TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_password_reset_token(user_id: uuid.UUID) -> str:
    return _create_token(str(user_id), TokenType.PASSWORD_RESET, timedelta(hours=1))


def decode_token(token: str) -> dict[str, Any]:
    """Raises jwt.PyJWTError (ExpiredSignatureError, InvalidTokenError, ...) on failure."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
