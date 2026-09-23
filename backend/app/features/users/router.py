import uuid

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_active_user, require_admin
from app.core.exceptions import ForbiddenError
from app.features.users.dependencies import get_address_service, get_user_service
from app.features.users.models import Address, User
from app.features.users.schemas import (
    AddressCreate,
    AddressRead,
    AddressUpdate,
    AdminUserCreate,
    AdminUserUpdate,
    UserProfileUpdate,
    UserRead,
)
from app.features.users.service import AddressService, UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_my_profile(user: User = Depends(get_current_active_user)) -> User:
    return user


@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.update_profile(user, payload)


@router.get("/me/addresses", response_model=list[AddressRead])
async def list_my_addresses(
    user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service),
) -> list[Address]:
    return await service.list_for_user(user.id)


@router.post("/me/addresses", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def add_my_address(
    payload: AddressCreate,
    user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service),
) -> Address:
    return await service.create_for_user(user.id, payload)


@router.patch("/me/addresses/{address_id}", response_model=AddressRead)
async def update_my_address(
    address_id: uuid.UUID,
    payload: AddressUpdate,
    user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service),
) -> Address:
    address = await service.get_or_404(address_id)
    if address.user_id != user.id:
        raise ForbiddenError("This address does not belong to you")
    return await service.update(address, payload)


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_address(
    address_id: uuid.UUID,
    user: User = Depends(get_current_active_user),
    service: AddressService = Depends(get_address_service),
) -> None:
    address = await service.get_or_404(address_id)
    if address.user_id != user.id:
        raise ForbiddenError("This address does not belong to you")
    await service.delete(address)


# Admin: full user management (PG-A002) — list/create/update/deactivate users.
# Bespoke (not `build_crud_router`) because a single "user" spans two tables
# (users, customers) — see UserService.create/update.
admin_router = APIRouter(
    prefix="/admin/users", tags=["admin:users"], dependencies=[Depends(require_admin)]
)


@admin_router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = 0, limit: int = 50, service: UserService = Depends(get_user_service)
) -> list[User]:
    return await service.list_all(skip=skip, limit=limit)


@admin_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, service: UserService = Depends(get_user_service)) -> User:
    return await service.get_or_404(user_id)


@admin_router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: AdminUserCreate, service: UserService = Depends(get_user_service)
) -> User:
    return await service.create(payload)


@admin_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    service: UserService = Depends(get_user_service),
) -> User:
    user = await service.get_or_404(user_id)
    return await service.update(user, payload)


@admin_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, service: UserService = Depends(get_user_service)) -> None:
    user = await service.get_or_404(user_id)
    await service.delete(user)


# NOTE: `admin_router` is exported separately (not nested under `router`, which
# already carries the `/users` prefix) to avoid double-prefixing —
# app/api/v1/router.py includes both directly.
