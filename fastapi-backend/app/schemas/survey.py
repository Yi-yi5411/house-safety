"""Pydantic schemas for survey-related operations — corrected to match Drizzle schema."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AIReasoningResult(BaseModel):
    """AI reasoning result structure."""

    conclusion: str | None = None
    basic_evaluation: str | None = None
    risk_level: str | None = None
    suggestion: str | None = None


class SurveyBase(BaseModel):
    """Base survey schema with common fields — matches Drizzle column types."""

    # --- 基本信息 ---
    project_name: str | None = Field(default=None, max_length=256)
    address: str | None = Field(default=None, max_length=255)
    build_year: str | None = Field(default=None, max_length=50)
    structure_type: str | None = Field(default=None, max_length=100)
    floor_count: int | None = None
    underground_floors: int | None = None
    build_area: Decimal | None = None
    land_area: Decimal | None = None
    building_height: Decimal | None = None
    usage: str | None = Field(default=None, max_length=128)
    usage_category: str | None = Field(default=None, max_length=64)
    owner_name: str | None = Field(default=None, max_length=128)
    owner_phone: str | None = Field(default=None, max_length=20)
    contact_person: str | None = Field(default=None, max_length=100)
    contact_phone: str | None = Field(default=None, max_length=50)
    foundation_type: str | None = Field(default=None, max_length=64)
    seismic_design_intensity: str | None = Field(default=None, max_length=32)
    roof_type: str | None = Field(default=None, max_length=64)
    wall_material: str | None = Field(default=None, max_length=128)
    survey_purpose: str | None = None  # Text field
    surveyor_name: str | None = Field(default=None, max_length=128)
    # New fields matching Drizzle
    survey_no: str | None = Field(default=None, max_length=100)
    survey_category: str | None = Field(default="整幢鉴定", max_length=100)
    survey_category_desc: str | None = None
    street: str | None = Field(default=None, max_length=255)
    community: str | None = Field(default=None, max_length=255)
    property_owner: str | None = Field(default=None, max_length=255)
    property_user: str | None = Field(default=None, max_length=255)
    client_name: str | None = Field(default=None, max_length=255)
    house_name: str | None = Field(default=None, max_length=255)
    property_nature: str | None = Field(default=None, max_length=100)
    property_certificate_no: str | None = Field(default=None, max_length=255)
    eaves_height: str | None = Field(default=None, max_length=50)
    design_usage: str | None = Field(default=None, max_length=100)
    survey_unit: str | None = Field(default=None, max_length=255)
    design_unit: str | None = Field(default=None, max_length=255)
    construction_unit: str | None = Field(default=None, max_length=255)
    supervision_unit: str | None = Field(default=None, max_length=255)
    current_usage: str | None = Field(default=None, max_length=100)
    usage_history: str | None = None
    external_environment: str | None = None
    evaluation_standards: str | None = None
    remark: str | None = None


class SurveyCreate(SurveyBase):
    """Schema for creating a new survey."""
    pass


class SurveyUpdate(BaseModel):
    """Schema for updating an existing survey (all fields optional)."""

    project_name: str | None = Field(default=None, max_length=256)
    address: str | None = Field(default=None, max_length=255)
    build_year: str | None = Field(default=None, max_length=50)
    structure_type: str | None = Field(default=None, max_length=100)
    floor_count: int | None = None
    underground_floors: int | None = None
    build_area: Decimal | None = None
    land_area: Decimal | None = None
    usage: str | None = Field(default=None, max_length=128)
    usage_category: str | None = Field(default=None, max_length=64)
    owner_name: str | None = Field(default=None, max_length=128)
    owner_phone: str | None = Field(default=None, max_length=20)
    contact_person: str | None = Field(default=None, max_length=100)
    contact_phone: str | None = Field(default=None, max_length=50)
    foundation_type: str | None = Field(default=None, max_length=64)
    seismic_design_intensity: str | None = Field(default=None, max_length=32)
    roof_type: str | None = Field(default=None, max_length=64)
    wall_material: str | None = Field(default=None, max_length=128)
    survey_purpose: str | None = None
    surveyor_name: str | None = Field(default=None, max_length=128)
    conclusion: str | None = None  # Text field
    basic_evaluation: str | None = None
    risk_level: str | None = Field(default=None, max_length=32)
    suggestion: str | None = None
    ai_reasoning_result: AIReasoningResult | None = None
    building_profile: dict | None = None
    status: str | None = Field(default=None, max_length=50)
    survey_no: str | None = Field(default=None, max_length=100)
    survey_category: str | None = None
    survey_category_desc: str | None = None
    site_plan_url: str | None = None
    street: str | None = None
    community: str | None = None
    property_owner: str | None = None
    property_user: str | None = None
    client_name: str | None = None
    entrust_date: datetime | None = None
    survey_date: datetime | None = None
    inspection_date: datetime | None = None
    inspection_complete_date: datetime | None = None
    house_name: str | None = None
    property_nature: str | None = None
    property_certificate_no: str | None = None
    building_height: Decimal | None = None
    eaves_height: str | None = Field(default=None, max_length=50)
    design_usage: str | None = None
    survey_unit: str | None = None
    design_unit: str | None = None
    construction_unit: str | None = None
    supervision_unit: str | None = None
    current_usage: str | None = Field(default=None, max_length=100)
    usage_history: str | None = None
    external_environment: str | None = None
    evaluation_standards: str | None = None
    is_rural_dangerous_repair: bool | None = None
    is_protected_building: bool | None = None
    is_historical_certificate: bool | None = None
    is_training_institution: bool | None = None
    is_self_building_special_report: bool | None = None
    is_self_building: bool | None = None
    is_commercial_self_building: bool | None = None
    census_house_no: str | None = None
    self_building_check_code: str | None = None
    remark: str | None = None


class SurveyResponse(SurveyBase):
    """Survey response schema."""

    id: uuid.UUID
    survey_time: datetime | None = None
    conclusion: str | None = None
    basic_evaluation: str | None = None
    risk_level: str | None = None
    suggestion: str | None = None
    ai_reasoning_result: dict | None = None
    building_profile: dict | None = None
    report_data: dict | None = None
    status: str
    creator_id: int | None = None
    report_url: str | None = None
    original_record_url: str | None = None
    site_plan_url: str | None = None
    entrust_date: datetime | None = None
    survey_date: datetime | None = None
    inspection_date: datetime | None = None
    inspection_complete_date: datetime | None = None
    is_rural_dangerous_repair: bool | None = None
    is_protected_building: bool | None = None
    is_historical_certificate: bool | None = None
    is_training_institution: bool | None = None
    is_self_building_special_report: bool | None = None
    is_self_building: bool | None = None
    is_commercial_self_building: bool | None = None
    census_house_no: str | None = None
    self_building_check_code: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SurveyListResponse(BaseModel):
    """Paginated survey list response."""

    items: list[SurveyResponse]
    total: int
    page: int = 1
    page_size: int = 20
