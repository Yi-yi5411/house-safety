"""Report template Pydantic schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReportTemplateCreate(BaseModel):
    """Payload for creating a report template."""

    name: str = Field(..., max_length=256)
    file_path: str = Field(..., description="OSS file path to the .docx template")


class ReportTemplateUpdate(BaseModel):
    """Payload for updating a report template."""

    name: str | None = Field(None, max_length=256)
    is_active: bool | None = None


class ReportTemplateResponse(BaseModel):
    """Report template response schema."""

    id: uuid.UUID
    name: str
    file_path: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportTemplateListResponse(BaseModel):
    """Paginated list of report templates."""

    items: list[ReportTemplateResponse]
    total: int
