import uuid

from pydantic import BaseModel, EmailStr, Field

from app.common.enums import UserRole
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


class UserRead(IDTimestampSchema):
    name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool


class UserProfileUpdate(BaseModel):
    """Self-service profile update — cannot change role/is_active/email verification here."""

    name: str | None = None
    phone: str | None = None


class AdminUserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    role: UserRole = UserRole.CUSTOMER


class AdminUserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
