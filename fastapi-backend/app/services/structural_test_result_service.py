"""CRUD operations for StructuralTestResult model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.structural_test_result import StructuralTestResult
from app.schemas.structural_test_result import (
    StructuralTestResultCreate,
    StructuralTestResultUpdate,
)


async def get_test_results_by_survey(
    db: AsyncSession,
    survey_id: UUID,
) -> list[StructuralTestResult]:
    """Get all test results for a survey."""
    stmt = (
        select(StructuralTestResult)
        .where(StructuralTestResult.survey_id == survey_id)
        .order_by(StructuralTestResult.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_test_result(
    db: AsyncSession,
    result_id: UUID,
) -> StructuralTestResult | None:
    """Get a single test result by ID."""
    stmt = select(StructuralTestResult).where(StructuralTestResult.id == result_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_test_result(
    db: AsyncSession,
    data: StructuralTestResultCreate,
) -> StructuralTestResult:
    """Create a new structural test result."""
    test_result = StructuralTestResult(**data.model_dump())
    db.add(test_result)
    await db.flush()
    await db.refresh(test_result)
    return test_result


async def update_test_result(
    db: AsyncSession,
    test_result: StructuralTestResult,
    data: StructuralTestResultUpdate,
) -> StructuralTestResult:
    """Update an existing structural test result."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(test_result, key, value)
    await db.flush()
    await db.refresh(test_result)
    return test_result


async def delete_test_result(
    db: AsyncSession,
    test_result: StructuralTestResult,
) -> None:
    """Delete a structural test result."""
    await db.delete(test_result)
    await db.flush()
