"""Pydantic schemas for ComponentTemplate (构件模板)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ComponentTemplateBase(BaseModel):
    """Shared ComponentTemplate properties."""

    category: str
    name: str
    check_items: list[Any]
    display_order: int | None = 0


class ComponentTemplateCreate(ComponentTemplateBase):
    """Schema for creating a component template."""

    pass


class ComponentTemplateUpdate(BaseModel):
    """Schema for updating a component template."""

    category: str | None = None
    name: str | None = None
    check_items: list[Any] | None = None
    display_order: int | None = None


class ComponentTemplateResponse(ComponentTemplateBase):
    """ComponentTemplate response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComponentTemplateListResponse(BaseModel):
    """ComponentTemplate list response."""

    items: list[ComponentTemplateResponse]
