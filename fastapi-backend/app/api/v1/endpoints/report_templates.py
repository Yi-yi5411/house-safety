"""Report template API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.report_template import ReportTemplate
from app.models.user import User
from app.schemas.report_template import (
    ReportTemplateCreate,
    ReportTemplateListResponse,
    ReportTemplateResponse,
    ReportTemplateUpdate,
)

router = APIRouter()


@router.get("/", response_model=ReportTemplateListResponse)
async def list_report_templates(
    db: AsyncSession = Depends(get_db),
) -> ReportTemplateListResponse:
    """List all report templates."""
    result = await db.execute(
        select(ReportTemplate).order_by(ReportTemplate.created_at.desc())
    )
    items = result.scalars().all()
    return ReportTemplateListResponse(
        items=[ReportTemplateResponse.model_validate(t) for t in items],
        total=len(items),
    )


@router.get("/active", response_model=ReportTemplateResponse)
async def get_active_template(
    db: AsyncSession = Depends(get_db),
) -> ReportTemplate:
    """Get the currently active report template."""
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.is_active == True)
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise NotFoundError(detail="No active template found")
    return template


@router.post(
    "/", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_report_template(
    payload: ReportTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportTemplate:
    """Create a new report template."""
    template = ReportTemplate(**payload.model_dump())
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


@router.put("/{template_id}/active", response_model=ReportTemplateResponse)
async def set_active_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportTemplate:
    """Set a template as the active one (deactivates others)."""
    # Deactivate all
    await db.execute(
        update(ReportTemplate).values(is_active=False)
    )
    # Activate target
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise NotFoundError(detail="Template not found")
    template.is_active = True
    await db.flush()
    await db.refresh(template)
    return template


@router.delete("/{template_id}")
async def delete_report_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a report template."""
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if template is None:
        raise NotFoundError(detail="Template not found")
    await db.delete(template)
    await db.flush()
