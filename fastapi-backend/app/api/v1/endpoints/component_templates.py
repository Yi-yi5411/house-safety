"""Component template API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.component_template import ComponentTemplate
from app.schemas.component_template import (
    ComponentTemplateListResponse,
    ComponentTemplateResponse,
)

router = APIRouter()


@router.get("/", response_model=ComponentTemplateListResponse)
async def list_component_templates(
    db: AsyncSession = Depends(get_db),
) -> ComponentTemplateListResponse:
    """List all component templates ordered by display order."""
    result = await db.execute(
        select(ComponentTemplate).order_by(ComponentTemplate.display_order)
    )
    items = result.scalars().all()
    return ComponentTemplateListResponse(
        items=[ComponentTemplateResponse.model_validate(t) for t in items],
        total=len(items),
    )
