"""Report signature API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.report_signature import ReportSignature
from app.models.user import User
from app.schemas.report_signature import (
    ReportSignatureCreate,
    ReportSignatureListResponse,
    ReportSignatureResponse,
    ReportSignatureUpdate,
)

router = APIRouter()


@router.get("/{survey_id}/signatures", response_model=ReportSignatureListResponse)
async def list_signatures(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ReportSignatureListResponse:
    """List signatures for a survey."""
    result = await db.execute(
        select(ReportSignature)
        .where(ReportSignature.survey_id == survey_id)
        .order_by(ReportSignature.created_at)
    )
    items = result.scalars().all()
    return ReportSignatureListResponse(
        items=[ReportSignatureResponse.model_validate(s) for s in items],
        total=len(items),
    )


@router.post(
    "/{survey_id}/signatures",
    response_model=ReportSignatureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_signature(
    survey_id: uuid.UUID,
    payload: ReportSignatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportSignature:
    """Create a new signature for a survey."""
    sig = ReportSignature(survey_id=survey_id, **payload.model_dump())
    db.add(sig)
    await db.flush()
    await db.refresh(sig)
    return sig


@router.put("/{survey_id}/signatures/{signature_id}", response_model=ReportSignatureResponse)
async def update_signature(
    survey_id: uuid.UUID,
    signature_id: uuid.UUID,
    payload: ReportSignatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportSignature:
    """Update a signature."""
    result = await db.execute(
        select(ReportSignature).where(
            ReportSignature.id == signature_id,
            ReportSignature.survey_id == survey_id,
        )
    )
    sig = result.scalar_one_or_none()
    if sig is None:
        raise NotFoundError(detail="Signature not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(sig, field, value)
    await db.flush()
    await db.refresh(sig)
    return sig


@router.delete("/{survey_id}/signatures/{signature_id}")
async def delete_signature(
    survey_id: uuid.UUID,
    signature_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a signature."""
    result = await db.execute(
        select(ReportSignature).where(
            ReportSignature.id == signature_id,
            ReportSignature.survey_id == survey_id,
        )
    )
    sig = result.scalar_one_or_none()
    if sig is None:
        raise NotFoundError(detail="Signature not found")
    await db.delete(sig)
    await db.flush()
