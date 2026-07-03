"""CRUD operations for EvaluationStandard model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_standard import EvaluationStandard
from app.schemas.evaluation_standard import (
    EvaluationStandardCreate,
    EvaluationStandardUpdate,
)


async def get_standards_by_category(
    db: AsyncSession,
    category: str,
) -> list[EvaluationStandard]:
    """Get evaluation standards filtered by category."""
    stmt = (
        select(EvaluationStandard)
        .where(EvaluationStandard.category == category)
        .order_by(EvaluationStandard.sort_order)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_all_standards(db: AsyncSession) -> list[EvaluationStandard]:
    """Get all evaluation standards."""
    stmt = select(EvaluationStandard).order_by(
        EvaluationStandard.category,
        EvaluationStandard.sort_order,
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_standard(db: AsyncSession, standard_id: UUID) -> EvaluationStandard | None:
    """Get a single standard by ID."""
    stmt = select(EvaluationStandard).where(EvaluationStandard.id == standard_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_standard(
    db: AsyncSession,
    data: EvaluationStandardCreate,
) -> EvaluationStandard:
    """Create a new evaluation standard."""
    standard = EvaluationStandard(**data.model_dump())
    db.add(standard)
    await db.flush()
    await db.refresh(standard)
    return standard


async def update_standard(
    db: AsyncSession,
    standard: EvaluationStandard,
    data: EvaluationStandardUpdate,
) -> EvaluationStandard:
    """Update an existing evaluation standard."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(standard, key, value)
    await db.flush()
    await db.refresh(standard)
    return standard


async def delete_standard(
    db: AsyncSession,
    standard: EvaluationStandard,
) -> None:
    """Delete an evaluation standard."""
    await db.delete(standard)
    await db.flush()
