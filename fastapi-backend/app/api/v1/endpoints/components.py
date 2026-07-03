"""Component check API endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.component_check import ComponentCheck
from app.models.evaluation_standard import EvaluationStandard
from app.models.user import User
from app.models.user import User
from app.schemas.component import (
    ComponentCheckBatchUpdate,
    ComponentCheckCreate,
    ComponentCheckListResponse,
    ComponentCheckResponse,
    ComponentCheckUpdate,
    EvaluationStandardCreate,
    EvaluationStandardListResponse,
    EvaluationStandardResponse,
    EvaluationStandardUpdate,
)

router = APIRouter()


# ---- Component Check endpoints ----


@router.get("/", response_model=ComponentCheckListResponse)
async def list_components(
    db: Annotated[AsyncSession, Depends(get_db)],
    survey_id: uuid.UUID | None = Query(None),
) -> ComponentCheckListResponse:
    """List component checks, optionally filtered by survey_id."""
    stmt = select(ComponentCheck).order_by(ComponentCheck.created_at.desc())
    if survey_id:
        stmt = stmt.where(ComponentCheck.survey_id == survey_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ComponentCheckListResponse(
        items=[ComponentCheckResponse.model_validate(c) for c in items]
    )


@router.post(
    "/", response_model=ComponentCheckResponse, status_code=status.HTTP_201_CREATED
)
async def create_component(
    payload: ComponentCheckCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ComponentCheck:
    """Create a new component check record."""
    component = ComponentCheck(
        **payload.model_dump(exclude_unset=True),
    )
    db.add(component)
    await db.flush()
    await db.refresh(component)
    return component


# ---- Evaluation Standard endpoints ----

@router.get("/standards", response_model=EvaluationStandardListResponse)
async def list_standards(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(None),
    component_type: str | None = Query(None, alias="componentType"),
) -> EvaluationStandardListResponse:
    """List evaluation standards, optionally filtered by category and/or componentType."""
    stmt = select(EvaluationStandard).order_by(EvaluationStandard.sort_order)
    if category:
        stmt = stmt.where(EvaluationStandard.category == category)
    if component_type:
        stmt = stmt.where(EvaluationStandard.component_type == component_type)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return EvaluationStandardListResponse(
        items=[EvaluationStandardResponse.model_validate(s) for s in items]
    )


@router.post(
    "/standards",
    response_model=EvaluationStandardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_standard(
    payload: EvaluationStandardCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EvaluationStandard:
    """Create a new evaluation standard."""
    standard = EvaluationStandard(**payload.model_dump(exclude_unset=True))
    db.add(standard)
    await db.flush()
    await db.refresh(standard)
    return standard


@router.put(
    "/standards/{standard_id}",
    response_model=EvaluationStandardResponse,
)
async def update_standard(
    standard_id: uuid.UUID,
    payload: EvaluationStandardUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EvaluationStandard:
    """Update an existing evaluation standard."""
    result = await db.execute(
        select(EvaluationStandard).where(EvaluationStandard.id == standard_id)
    )
    standard = result.scalar_one_or_none()
    if standard is None:
        raise NotFoundError(detail="Evaluation standard not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(standard, field, value)
    await db.flush()
    await db.refresh(standard)
    return standard


@router.delete("/standards/{standard_id}")
async def delete_standard(
    standard_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an evaluation standard."""
    result = await db.execute(
        select(EvaluationStandard).where(EvaluationStandard.id == standard_id)
    )
    standard = result.scalar_one_or_none()
    if standard is None:
        raise NotFoundError(detail="Evaluation standard not found")
    await db.delete(standard)
    await db.flush()


@router.get("/{component_id}", response_model=ComponentCheckResponse)
async def get_component(
    component_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ComponentCheck:
    """Get a single component check by ID."""
    result = await db.execute(
        select(ComponentCheck).where(ComponentCheck.id == component_id)
    )
    component = result.scalar_one_or_none()
    if component is None:
        raise NotFoundError(detail="Component check not found")
    return component


@router.put("/{component_id}", response_model=ComponentCheckResponse)
async def update_component(
    component_id: uuid.UUID,
    payload: ComponentCheckUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ComponentCheck:
    """Update an existing component check."""
    result = await db.execute(
        select(ComponentCheck).where(ComponentCheck.id == component_id)
    )
    component = result.scalar_one_or_none()
    if component is None:
        raise NotFoundError(detail="Component check not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(component, field, value)
    await db.flush()
    await db.refresh(component)
    return component


@router.put("/batch", response_model=ComponentCheckListResponse)
async def batch_update_components(
    payload: ComponentCheckBatchUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ComponentCheckListResponse:
    """Batch update component checks.

    Each item in the list must include its `id` plus the fields to update.
    """
    updated_items: list[ComponentCheck] = []
    for item in payload.items:
        result = await db.execute(
            select(ComponentCheck).where(ComponentCheck.id == item.id)
        )
        component = result.scalar_one_or_none()
        if component is None:
            continue  # Skip missing items; could also raise per-item errors
        update_data = item.model_dump(exclude_unset=True, exclude={"id"})
        for field, value in update_data.items():
            setattr(component, field, value)
        updated_items.append(component)
    if updated_items:
        await db.flush()
    return ComponentCheckListResponse(
        items=[ComponentCheckResponse.model_validate(c) for c in updated_items]
    )


@router.delete("/{component_id}")
async def delete_component(
    component_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a component check record."""
    result = await db.execute(
        select(ComponentCheck).where(ComponentCheck.id == component_id)
    )
    component = result.scalar_one_or_none()
    if component is None:
        raise NotFoundError(detail="Component check not found")
    await db.delete(component)
    await db.flush()
