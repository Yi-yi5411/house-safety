"""Pydantic schemas for EvaluationStandard (评定标准)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EvaluationStandardBase(BaseModel):
    """Shared EvaluationStandard properties."""

    category: str
    component_type: str
    description: str
    evaluation_result: str | None = None
    evaluation_clause: str | None = None
    sort_order: int | None = 0


class EvaluationStandardCreate(EvaluationStandardBase):
    """Schema for creating an evaluation standard."""

    pass


class EvaluationStandardUpdate(BaseModel):
    """Schema for updating an evaluation standard."""

    category: str | None = None
    component_type: str | None = None
    description: str | None = None
    evaluation_result: str | None = None
    evaluation_clause: str | None = None
    sort_order: int | None = None


class EvaluationStandardResponse(EvaluationStandardBase):
    """EvaluationStandard response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvaluationStandardListResponse(BaseModel):
    """EvaluationStandard list response."""

    items: list[EvaluationStandardResponse]
