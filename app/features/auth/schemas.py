from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class LogoutRequest(BaseModel):
    refresh_token: str
