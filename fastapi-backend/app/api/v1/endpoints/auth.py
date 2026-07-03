"""Authentication API endpoints."""

from __future__ import annotations

import random
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import AuthenticationError, DuplicateError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    Token,
    UserEmailCodeSend,
    UserEmailLogin,
    UserEmailRegister,
    UserPhoneCodeSend,
    UserPhoneLogin,
    UserResponse,
    UserWeChatLogin,
)
from app.utils.email_utils import send_email_code
from app.utils.redis_client import cache_delete, cache_get, cache_set
from app.utils.sms import send_sms_code
from app.utils.wechat import code_to_session

router = APIRouter()

# Redis key prefixes and expiry
EMAIL_CODE_PREFIX = "email:code:"
PHONE_CODE_PREFIX = "phone:code:"
CODE_EXPIRE = 300  # 5 minutes


def _generate_code() -> str:
    """Generate a 6-digit random verification code."""
    return f"{random.randint(100000, 999999)}"


@router.post("/email/send", status_code=status.HTTP_200_OK)
async def send_email_verification_code(
    payload: UserEmailCodeSend,
) -> dict[str, str]:
    """Send a 6-digit verification code to the given email."""
    code = _generate_code()
    redis_key = f"{EMAIL_CODE_PREFIX}{payload.email}"
    await cache_set(redis_key, code, expire=CODE_EXPIRE)
    await send_email_code(payload.email, code)
    return {"message": "Verification code sent"}


# ---- Phone SMS auth ----

@router.post("/phone/send", status_code=status.HTTP_200_OK)
async def send_phone_verification_code(
    payload: UserPhoneCodeSend,
) -> dict[str, str]:
    """Send a 6-digit SMS verification code to the given phone."""
    code = await send_sms_code(payload.phone)
    redis_key = f"{PHONE_CODE_PREFIX}{payload.phone}"
    await cache_set(redis_key, code, expire=CODE_EXPIRE)
    return {"message": "Verification code sent"}


@router.post("/login/phone", response_model=Token)
async def phone_login(
    payload: UserPhoneLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Authenticate with phone and SMS verification code, return JWT token."""
    redis_key = f"{PHONE_CODE_PREFIX}{payload.phone}"
    stored_code = await cache_get(redis_key)

    if stored_code is None or stored_code != payload.code:
        raise AuthenticationError(detail="Invalid or expired verification code")

    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()

    if user is None:
        # Auto-register new phone user
        user = User(phone=payload.phone)
        db.add(user)
        await db.flush()

    # Consume the code
    await cache_delete(redis_key)

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}


# ---- Email auth ----

@router.post("/login/email", response_model=Token)
async def email_login(
    payload: UserEmailLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Authenticate with email and verification code, return JWT token."""
    redis_key = f"{EMAIL_CODE_PREFIX}{payload.email}"
    stored_code = await cache_get(redis_key)

    if stored_code is None or stored_code != payload.code:
        raise AuthenticationError(detail="Invalid or expired verification code")

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthenticationError(detail="Email not registered")

    # Consume the code
    await cache_delete(redis_key)

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserEmailRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Register a new user with email and verification code."""
    redis_key = f"{EMAIL_CODE_PREFIX}{payload.email}"
    stored_code = await cache_get(redis_key)

    if stored_code is None or stored_code != payload.code:
        raise AuthenticationError(detail="Invalid or expired verification code")

    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise DuplicateError(detail="Email already registered")

    user = User(
        email=payload.email,
        nickname=payload.nickname,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Consume the code
    await cache_delete(redis_key)
    return user


@router.post("/login", response_model=Token)
async def login(
    payload: UserEmailLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Authenticate with email and verification code, return JWT token."""
    redis_key = f"{EMAIL_CODE_PREFIX}{payload.email}"
    stored_code = await cache_get(redis_key)

    if stored_code is None or stored_code != payload.code:
        raise AuthenticationError(detail="Invalid or expired verification code")

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthenticationError(detail="Email not registered")

    # Consume the code
    await cache_delete(redis_key)

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/wechat/login", response_model=Token)
async def wechat_login(
    payload: UserWeChatLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Login via WeChat Mini Program code, return JWT token."""
    session_data = await code_to_session(payload.code)
    openid = session_data.get("openid")
    unionid = session_data.get("unionid")

    result = await db.execute(
        select(User).where(User.wechat_open_id == openid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            wechat_open_id=openid,
            wechat_union_id=unionid,
        )
        db.add(user)
        await db.flush()

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the current authenticated user's profile."""
    return current_user
