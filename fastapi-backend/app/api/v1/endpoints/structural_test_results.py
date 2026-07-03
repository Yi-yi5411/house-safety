"""Structural test result API endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.structural_test_result import StructuralTestResult
from app.models.user import User
from app.schemas.structural_test_result import (
    StructuralTestResultCreate,
    StructuralTestResultResponse,
    StructuralTestResultListResponse,
    StructuralTestResultUpdate,
)

router = APIRouter()


@router.get(
    "/{survey_id}/structural-test-results",
    response_model=StructuralTestResultListResponse,
)
async def list_test_results(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StructuralTestResultListResponse:
    """List structural test results for a survey."""
    result = await db.execute(
        select(StructuralTestResult)
        .where(StructuralTestResult.survey_id == survey_id)
        .order_by(StructuralTestResult.created_at.desc())
    )
    items = result.scalars().all()
    return StructuralTestResultListResponse(
        items=[StructuralTestResultResponse.model_validate(r) for r in items],
        total=len(items),
    )


@router.post(
    "/{survey_id}/structural-test-results",
    response_model=StructuralTestResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_result(
    survey_id: uuid.UUID,
    payload: StructuralTestResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StructuralTestResult:
    """Create or update (upsert) a structural test result.

    If a test result already exists for this survey, updates it.
    Otherwise creates a new one. Matches old NestJS upsert behavior.
    """
    # Check if a test result already exists for this survey
    existing = await db.execute(
        select(StructuralTestResult).where(
            StructuralTestResult.survey_id == survey_id
        )
    )
    record = existing.scalar_one_or_none()

    if record:
        # Update existing
        update_data = payload.model_dump(
            exclude_unset=True, exclude={"survey_id"}
        )
        for field, value in update_data.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
    else:
        # Create new
        data = payload.model_dump()
        data["survey_id"] = survey_id
        record = StructuralTestResult(**data)
        db.add(record)
        await db.flush()
        await db.refresh(record)
    return record


@router.put(
    "/{survey_id}/structural-test-results/{result_id}",
    response_model=StructuralTestResultResponse,
)
async def update_test_result(
    survey_id: uuid.UUID,
    result_id: uuid.UUID,
    payload: StructuralTestResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StructuralTestResult:
    """Update a structural test result."""
    result = await db.execute(
        select(StructuralTestResult).where(
            StructuralTestResult.id == result_id,
            StructuralTestResult.survey_id == survey_id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise NotFoundError(detail="Test result not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/{survey_id}/structural-test-results/{result_id}")
async def delete_test_result(
    survey_id: uuid.UUID,
    result_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a structural test result."""
    result = await db.execute(
        select(StructuralTestResult).where(
            StructuralTestResult.id == result_id,
            StructuralTestResult.survey_id == survey_id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise NotFoundError(detail="Test result not found")
    await db.delete(record)
    await db.flush()
