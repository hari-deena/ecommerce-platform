from fastapi import APIRouter, Depends, status

from app.features.auth.dependencies import get_auth_service
from app.features.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.features.auth.service import AuthService
from app.features.users.models import User
from app.features.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest, service: AuthService = Depends(get_auth_service)
) -> User:
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return await service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return await service.refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest, service: AuthService = Depends(get_auth_service)
) -> None:
    await service.logout(payload.refresh_token)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    payload: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)
) -> dict[str, str]:
    await service.forgot_password(payload.email)
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)
) -> None:
    await service.reset_password(payload.token, payload.new_password)
