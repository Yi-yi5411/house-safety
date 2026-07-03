"""Pydantic schemas for StructuralTestResult (结构检测结果)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StructuralTestResultCreate(BaseModel):
    """Schema for creating a structural test result (survey_id from payload)."""

    survey_id: UUID
    test_unit: str | None = None
    certificate_no: str | None = None
    test_personnel: str | None = None
    report_no: str | None = None
    test_date: datetime | None = None
    main_test_content: str | None = None
    test_standards: str | None = None
    test_results_summary: str | None = None
    damage_summary: str | None = None
    cause_analysis: str | None = None
    conclusion: str | None = None
    handling_suggestion: str | None = None
    safety_level: str | None = None


class StructuralTestResultUpdate(BaseModel):
    """Schema for updating a structural test result."""

    test_unit: str | None = None
    certificate_no: str | None = None
    test_personnel: str | None = None
    report_no: str | None = None
    test_date: datetime | None = None
    main_test_content: str | None = None
    test_standards: str | None = None
    test_results_summary: str | None = None
    damage_summary: str | None = None
    cause_analysis: str | None = None
    conclusion: str | None = None
    handling_suggestion: str | None = None
    safety_level: str | None = None


class StructuralTestResultResponse(BaseModel):
    """StructuralTestResult response schema."""

    id: UUID
    survey_id: UUID
    test_unit: str | None = None
    certificate_no: str | None = None
    test_personnel: str | None = None
    report_no: str | None = None
    test_date: datetime | None = None
    main_test_content: str | None = None
    test_standards: str | None = None
    test_results_summary: str | None = None
    damage_summary: str | None = None
    cause_analysis: str | None = None
    conclusion: str | None = None
    handling_suggestion: str | None = None
    safety_level: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StructuralTestResultListResponse(BaseModel):
    """StructuralTestResult list response."""

    items: list[StructuralTestResultResponse]
