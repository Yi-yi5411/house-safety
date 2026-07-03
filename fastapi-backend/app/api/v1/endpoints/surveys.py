"""Survey (鉴定记录) API endpoints — full CRUD."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.survey import Survey
from app.models.user import User
from app.schemas.survey import (
    SurveyCreate,
    SurveyListResponse,
    SurveyResponse,
    SurveyUpdate,
)
from app.services.report_service import generate_report_docx
from app.services.original_record_service import generate_original_record_docx

router = APIRouter()


@router.get("/", response_model=SurveyListResponse)
async def list_surveys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    keyword: str | None = Query(None, description="Search by address, client name, or house name"),
) -> SurveyListResponse:
    """List surveys with pagination and optional filters."""
    from sqlalchemy import or_

    conditions = [Survey.is_deleted == False]
    if status_filter:
        conditions.append(Survey.status == status_filter)
    if keyword:
        conditions.append(
            or_(
                Survey.address.ilike(f"%{keyword}%"),
                Survey.client_name.ilike(f"%{keyword}%"),
                Survey.house_name.ilike(f"%{keyword}%"),
            )
        )

    count_stmt = (
        select(func.count())
        .select_from(Survey)
        .where(*conditions)
    )
    total = (await db.execute(count_stmt)).scalar() or 0

    offset = (page - 1) * page_size
    query = (
        select(Survey)
        .where(*conditions)
        .order_by(Survey.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return SurveyListResponse(
        items=[SurveyResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED
)
async def create_survey(
    payload: SurveyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Survey:
    """Create a new survey record."""
    survey = Survey(
        **payload.model_dump(exclude_unset=True),
        creator_id=current_user.id,
    )
    db.add(survey)
    await db.flush()
    await db.refresh(survey)
    return survey


@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Survey:
    """Get a single survey by ID."""
    result = await db.execute(
        select(Survey).where(
            Survey.id == survey_id, Survey.is_deleted == False
        )
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")
    return survey


@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(
    survey_id: uuid.UUID,
    payload: SurveyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Survey:
    """Update an existing survey."""
    result = await db.execute(
        select(Survey).where(
            Survey.id == survey_id, Survey.is_deleted == False
        )
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(survey, field, value)
    await db.flush()
    await db.refresh(survey)
    return survey


@router.delete("/{survey_id}")
async def delete_survey(
    survey_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Soft-delete a survey by marking is_deleted=True."""
    result = await db.execute(
        select(Survey).where(
            Survey.id == survey_id, Survey.is_deleted == False
        )
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")
    survey.is_deleted = True
    await db.flush()


@router.post("/{survey_id}/generate-report")
async def generate_report(
    survey_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Trigger report generation for a survey. Returns the report ID."""
    # Verify survey exists
    result = await db.execute(
        select(Survey).where(Survey.id == survey_id, Survey.is_deleted == False)
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")
    # Report ID is the survey ID
    return {"reportId": str(survey_id)}


@router.post("/{survey_id}/generate-original-record")
async def generate_original_record(
    survey_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Trigger original record generation for a survey. Returns the record ID."""
    result = await db.execute(
        select(Survey).where(Survey.id == survey_id, Survey.is_deleted == False)
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")
    return {"recordId": str(survey_id)}
