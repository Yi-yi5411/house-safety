"""CRUD operations for ComponentCheck model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.component_check import ComponentCheck
from app.schemas.component_check import ComponentCheckCreate, ComponentCheckUpdate


async def get_component_checks_by_survey(
    db: AsyncSession,
    survey_id: UUID,
) -> list[ComponentCheck]:
    """Get all component checks for a survey."""
    stmt = (
        select(ComponentCheck)
        .where(ComponentCheck.survey_id == survey_id)
        .order_by(ComponentCheck.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_component_check(
    db: AsyncSession,
    check_id: UUID,
) -> ComponentCheck | None:
    """Get a single component check by ID."""
    stmt = select(ComponentCheck).where(ComponentCheck.id == check_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_component_check(
    db: AsyncSession,
    data: ComponentCheckCreate,
) -> ComponentCheck:
    """Create a new component check."""
    check = ComponentCheck(**data.model_dump())
    db.add(check)
    await db.flush()
    await db.refresh(check)
    return check


async def update_component_check(
    db: AsyncSession,
    check: ComponentCheck,
    data: ComponentCheckUpdate,
) -> ComponentCheck:
    """Update an existing component check."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(check, key, value)
    await db.flush()
    await db.refresh(check)
    return check


async def delete_component_check(
    db: AsyncSession,
    check: ComponentCheck,
) -> None:
    """Delete a component check."""
    await db.delete(check)
    await db.flush()
