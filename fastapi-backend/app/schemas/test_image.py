"""Pydantic schemas for TestImage (检测图片)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TestImageBase(BaseModel):
    """Shared TestImage properties."""

    survey_id: UUID
    type: str
    label: str | None = None
    image_url: str
    sort_order: int | None = 0


class TestImageCreate(BaseModel):
    """Schema for creating a test image (survey_id comes from URL)."""

    type: str
    label: str | None = None
    image_url: str
    sort_order: int | None = 0


class TestImageUpdate(BaseModel):
    """Schema for updating a test image."""

    type: str | None = None
    label: str | None = None
    image_url: str | None = None
    sort_order: int | None = None


class TestImageResponse(TestImageBase):
    """TestImage response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestImageReorderItem(BaseModel):
    """A single reorder item."""

    id: UUID
    sort_order: int


class TestImageReorderRequest(BaseModel):
    """Request to reorder test images."""

    items: list[TestImageReorderItem]


class TestImageListResponse(BaseModel):
    """TestImage list response."""

    items: list[TestImageResponse]
    total: int = 0
