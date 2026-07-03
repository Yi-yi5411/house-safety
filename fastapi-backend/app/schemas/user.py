"""Pydantic schemas for user-related operations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    nickname: str | None = Field(default=None, max_length=128)
    avatar_url: str | None = Field(default=None)


class UserCreate(UserBase):
    """Schema for creating a user via email + password."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class UserWeChatLogin(BaseModel):
    """Schema for WeChat login."""

    code: str = Field(..., description="WeChat login code")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    nickname: str | None = Field(default=None, max_length=128)
    avatar_url: str | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=255)


class UserInDB(UserBase):
    """User schema as stored in the database."""

    id: int
    wechat_open_id: str | None = None
    wechat_union_id: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserResponse(UserInDB):
    """User response schema (excludes sensitive fields)."""

    pass


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: str | None = None
    exp: int | None = None


class UserEmailCodeSend(BaseModel):
    """Schema for sending email verification code."""

    email: EmailStr = Field(..., max_length=255)


class UserEmailLogin(BaseModel):
    """Schema for email + verification code login."""

    email: EmailStr = Field(..., max_length=255)
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class UserEmailRegister(BaseModel):
    """Schema for email + verification code registration."""

    email: EmailStr = Field(..., max_length=255)
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    nickname: str | None = Field(default=None, max_length=128)


# ---- Phone / SMS auth schemas ----


class UserPhoneCodeSend(BaseModel):
    """Schema for sending SMS verification code."""

    phone: str = Field(..., max_length=20, description="Phone number")


class UserPhoneLogin(BaseModel):
    """Schema for phone + SMS verification code login."""

    phone: str = Field(..., max_length=20)
    code: str = Field(..., min_length=6, max_length=6, description="6-digit SMS code")
