"""Common Pydantic schemas used across the application."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int = 1
    page_size: int = 20


class UploadResponse(BaseModel):
    """File upload response."""

    file_url: str
    file_name: str
    file_size: int


class AIReasonRequest(BaseModel):
    """AI reasoning request payload."""

    survey_id: str
    prompt: str | None = None


class AIReasonResponse(BaseModel):
    """AI reasoning response payload."""

    conclusion: str | None = None
    basic_evaluation: str | None = None
    risk_level: str | None = None
    suggestion: str | None = None
    raw_output: str | None = None
