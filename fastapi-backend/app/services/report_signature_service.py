"""CRUD operations for ReportSignature model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report_signature import ReportSignature
from app.schemas.report_signature import (
    ReportSignatureCreate,
    ReportSignatureUpdate,
)


async def get_signatures_by_survey(
    db: AsyncSession,
    survey_id: UUID,
) -> list[ReportSignature]:
    """Get all signatures for a survey."""
    stmt = (
        select(ReportSignature)
        .where(ReportSignature.survey_id == survey_id)
        .order_by(ReportSignature.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_signature(
    db: AsyncSession,
    signature_id: UUID,
) -> ReportSignature | None:
    """Get a single signature by ID."""
    stmt = select(ReportSignature).where(ReportSignature.id == signature_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_signature(
    db: AsyncSession,
    data: ReportSignatureCreate,
) -> ReportSignature:
    """Create a new report signature."""
    signature = ReportSignature(**data.model_dump())
    db.add(signature)
    await db.flush()
    await db.refresh(signature)
    return signature


async def update_signature(
    db: AsyncSession,
    signature: ReportSignature,
    data: ReportSignatureUpdate,
) -> ReportSignature:
    """Update an existing report signature."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(signature, key, value)
    await db.flush()
    await db.refresh(signature)
    return signature


async def delete_signature(
    db: AsyncSession,
    signature: ReportSignature,
) -> None:
    """Delete a report signature."""
    await db.delete(signature)
    await db.flush()
