"""Pydantic schemas for ReportSignature (报告签名)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportSignatureBase(BaseModel):
    """Shared ReportSignature properties."""

    type: str
    signatory_name: str | None = None
    image_url: str | None = None
    sign_date: datetime | None = None


class ReportSignatureCreate(BaseModel):
    """Schema for creating a report signature (survey_id comes from URL)."""

    type: str
    signatory_name: str | None = None
    image_url: str | None = None
    sign_date: datetime | None = None


class ReportSignatureUpdate(BaseModel):
    """Schema for updating a report signature."""

    type: str | None = None
    signatory_name: str | None = None
    image_url: str | None = None
    sign_date: datetime | None = None


class ReportSignatureResponse(BaseModel):
    """ReportSignature response schema."""

    id: UUID
    survey_id: UUID
    type: str
    signatory_name: str | None = None
    image_url: str | None = None
    sign_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReportSignatureListResponse(BaseModel):
    """ReportSignature list response."""

    items: list[ReportSignatureResponse]
