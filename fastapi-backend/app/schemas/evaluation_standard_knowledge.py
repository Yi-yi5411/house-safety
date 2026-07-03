"""Pydantic schemas for EvaluationStandardKnowledge (鉴定依据标准知识库)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EvaluationStandardKnowledgeBase(BaseModel):
    """Shared EvaluationStandardKnowledge properties."""

    name: str
    code: str
    type: str
    content: str | None = None
    is_default: bool = False


class EvaluationStandardKnowledgeCreate(EvaluationStandardKnowledgeBase):
    """Schema for creating a knowledge entry."""

    pass


class EvaluationStandardKnowledgeUpdate(BaseModel):
    """Schema for updating a knowledge entry."""

    name: str | None = None
    code: str | None = None
    type: str | None = None
    content: str | None = None
    is_default: bool | None = None


class EvaluationStandardKnowledgeResponse(EvaluationStandardKnowledgeBase):
    """EvaluationStandardKnowledge response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvaluationStandardKnowledgeListResponse(BaseModel):
    """EvaluationStandardKnowledge list response."""

    items: list[EvaluationStandardKnowledgeResponse]
