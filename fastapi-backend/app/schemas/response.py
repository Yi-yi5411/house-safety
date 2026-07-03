"""Standardized API response schemas."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper.

    All endpoints return this structure so the frontend can reliably
    parse responses as {code, message, data}.
    """

    code: int = 200
    message: str = "success"
    data: T | None = None
