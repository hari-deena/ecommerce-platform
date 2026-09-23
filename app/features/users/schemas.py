import uuid
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.common.enums import RoleName
from app.common.schemas import IDTimestampSchema


class AddressBase(BaseModel):
    label: str = "home"
    line1: str
    line2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    label: str | None = None
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool | None = None


class AddressRead(AddressBase, IDTimestampSchema):
    user_id: uuid.UUID


class CustomerRead(IDTimestampSchema):
    user_id: uuid.UUID
    full_name: str
    phone: str | None


class UserRead(IDTimestampSchema):
    email: EmailStr
    is_active: bool
    role: RoleName
    customer: CustomerRead | None = None

    @field_validator("role", mode="before")
    @classmethod
    def _role_name(cls, value: Any) -> str:
        """`user.role` is a `Role` ORM object (via the `role_id` FK), not a plain string."""
        return getattr(value, "name", value)


class UserProfileUpdate(BaseModel):
    """Self-service profile update — operates on the linked `Customer` row,
    not `User` itself (which only holds auth identity + role)."""

    full_name: str | None = None
    phone: str | None = None


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    phone: str | None = None
    role: RoleName = RoleName.USER


class AdminUserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    role: RoleName | None = None
