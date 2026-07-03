"""Pydantic schemas for component-related operations."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class ComponentCheckBase(BaseModel):
    """Base component check schema.  Accepts both snake_case and camelCase."""

    model_config = {"populate_by_name": True, "alias_generator": to_camel}

    name: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=100)
    component_type: str | None = Field(default=None, max_length=100)
    axis_line: str | None = Field(default=None, max_length=100)
    floor_location: str | None = Field(default=None, max_length=64)
    position_desc: str | None = Field(default=None, max_length=256)
    damage_description: str | None = None
    damage_level: str | None = Field(default=None, max_length=32)
    crack_width: float | None = None
    crack_length: float | None = None
    deformation_value: float | None = None
    corrosion_degree: str | None = Field(default=None, max_length=32)
    checked_item_ids: list | None = None
    description_values: dict | None = None
    ai_evaluation_result: str | None = None
    ai_evaluation_clause: str | None = None
    remark: str | None = None


class ComponentCheckCreate(ComponentCheckBase):
    """Schema for creating a component check."""

    survey_id: uuid.UUID
    checked_item_ids: list | None = None
    photos: list[str] | None = None


class ComponentCheckUpdate(BaseModel):
    """Schema for updating a component check.  Accepts both snake_case and camelCase."""

    model_config = {"populate_by_name": True, "alias_generator": to_camel}

    name: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=100)
    component_type: str | None = Field(default=None, max_length=100)
    axis_line: str | None = Field(default=None, max_length=100)
    floor_location: str | None = Field(default=None, max_length=64)
    position_desc: str | None = Field(default=None, max_length=256)
    checked_item_ids: list | None = None
    description_values: dict | None = None
    damage_description: str | None = None
    damage_level: str | None = Field(default=None, max_length=32)
    crack_width: float | None = None
    crack_length: float | None = None
    deformation_value: float | None = None
    corrosion_degree: str | None = Field(default=None, max_length=32)
    ai_evaluation_result: str | None = Field(default=None, max_length=255)
    ai_evaluation_clause: str | None = Field(default=None, max_length=255)
    photos: list[str] | None = None
    remark: str | None = None


class ComponentCheckResponse(ComponentCheckBase):
    """Component check response schema."""

    id: uuid.UUID
    survey_id: uuid.UUID
    checked_item_ids: list | None = None
    description_values: dict | None = None
    ai_evaluation_result: str | None = None
    ai_evaluation_clause: str | None = None
    photos: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ComponentCheckListResponse(BaseModel):
    """Component check list response."""

    items: list[ComponentCheckResponse]


class EvaluationStandardBase(BaseModel):
    """Base evaluation standard schema."""

    category: str | None = Field(default=None, max_length=100)
    component_type: str | None = Field(default=None, max_length=100)
    description: str | None = None
    evaluation_result: str | None = Field(default=None, max_length=255)
    evaluation_clause: str | None = Field(default=None, max_length=255)
    sort_order: int = 0


class EvaluationStandardCreate(EvaluationStandardBase):
    """Schema for creating an evaluation standard."""

    pass


class EvaluationStandardUpdate(BaseModel):
    """Schema for updating an evaluation standard."""

    category: str | None = Field(default=None, max_length=100)
    component_type: str | None = Field(default=None, max_length=100)
    description: str | None = None
    evaluation_result: str | None = Field(default=None, max_length=255)
    evaluation_clause: str | None = Field(default=None, max_length=255)
    sort_order: int | None = None


class EvaluationStandardResponse(EvaluationStandardBase):
    """Evaluation standard response schema."""

    id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ComponentCheckBatchItem(BaseModel):
    """Single item in a batch update request."""

    id: uuid.UUID
    name: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=100)
    component_type: str | None = Field(default=None, max_length=100)
    axis_line: str | None = Field(default=None, max_length=100)
    floor_location: str | None = Field(default=None, max_length=64)
    position_desc: str | None = Field(default=None, max_length=256)
    checked_item_ids: list | None = None
    damage_description: str | None = None
    damage_level: str | None = Field(default=None, max_length=32)
    crack_width: float | None = None
    crack_length: float | None = None
    deformation_value: float | None = None
    corrosion_degree: str | None = Field(default=None, max_length=32)
    ai_evaluation_result: str | None = Field(default=None, max_length=255)
    ai_evaluation_clause: str | None = Field(default=None, max_length=255)
    photos: list[str] | None = None
    remark: str | None = None


class ComponentCheckBatchUpdate(BaseModel):
    """Schema for batch updating component checks."""

    items: list[ComponentCheckBatchItem]


class EvaluationStandardListResponse(BaseModel):
    """Evaluation standard list response."""

    items: list[EvaluationStandardResponse]
