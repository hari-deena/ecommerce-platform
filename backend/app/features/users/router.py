import uuid

from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_active_user
from app.common.crud_router import build_crud_router
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
admin_router = build_crud_router(
    service_dependency=get_user_service,
    create_schema=AdminUserCreate,
    update_schema=AdminUserUpdate,
    read_schema=UserRead,
    prefix="/admin/users",
    tags=["admin:users"],
    require_admin_read=True,
    require_admin_write=True,
)
# NOTE: `admin_router` is exported separately (not nested under `router`, which
# already carries the `/users` prefix) to avoid double-prefixing —
# app/api/v1/router.py includes both directly.
