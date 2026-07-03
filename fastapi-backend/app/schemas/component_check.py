"""Pydantic schemas for ComponentCheck (构件检查记录)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ComponentCheckBase(BaseModel):
    """Shared ComponentCheck properties."""

    survey_id: UUID
    name: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    axis_line: str | None = Field(default=None, max_length=100)
    checked_item_ids: list | None = None
    description_values: dict | None = None
    ai_evaluation_result: str | None = Field(default=None, max_length=255)
    ai_evaluation_clause: str | None = Field(default=None, max_length=255)
    photos: list[str] | None = None


class ComponentCheckCreate(ComponentCheckBase):
    """Schema for creating a component check."""

    pass


class ComponentCheckUpdate(BaseModel):
    """Schema for updating a component check."""

    name: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    axis_line: str | None = Field(default=None, max_length=100)
    checked_item_ids: list | None = None
    description_values: dict | None = None
    ai_evaluation_result: str | None = Field(default=None, max_length=255)
    ai_evaluation_clause: str | None = Field(default=None, max_length=255)
    photos: list[str] | None = None


class ComponentCheckResponse(ComponentCheckBase):
    """ComponentCheck response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComponentCheckListResponse(BaseModel):
    """ComponentCheck list response."""

    items: list[ComponentCheckResponse]
