"""Evaluation standards API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.evaluation_standard import EvaluationStandard
from app.schemas.component import (
    EvaluationStandardListResponse,
    EvaluationStandardResponse,
)

router = APIRouter()


@router.get("/", response_model=EvaluationStandardListResponse)
async def list_evaluation_standards(
    db: AsyncSession = Depends(get_db),
    category: str | None = Query(None, description="Filter by category"),
    component_type: str | None = Query(
        None, alias="componentType", description="Filter by component type"
    ),
) -> EvaluationStandardListResponse:
    """List evaluation standards with optional filters."""
    stmt = select(EvaluationStandard).order_by(EvaluationStandard.sort_order)

    if category:
        stmt = stmt.where(EvaluationStandard.category == category)
    if component_type:
        stmt = stmt.where(EvaluationStandard.component_type == component_type)

    result = await db.execute(stmt)
    items = result.scalars().all()
    return EvaluationStandardListResponse(
        items=[EvaluationStandardResponse.model_validate(s) for s in items],
        total=len(items),
    )
