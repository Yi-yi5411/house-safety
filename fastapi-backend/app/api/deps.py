"""API dependency injection helpers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Extract and validate the current user from the JWT bearer token.

    Raises:
        AuthenticationError: If the token is invalid or the user is not found.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise AuthenticationError(detail=str(exc)) from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError(detail="Invalid token payload")

    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthenticationError(detail="User not found")
    if not user.is_active:
        raise AuthenticationError(detail="Inactive user")
    return user


async def get_optional_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security_scheme)
    ] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> User | None:
    """Return the current user if a valid token is present, else None."""
    if credentials is None or db is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        return None
