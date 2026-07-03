"""CRUD operations for Survey model."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyUpdate


async def get_survey_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Survey], int]:
    """Get paginated survey list with total count."""
    count_stmt = select(func.count()).select_from(Survey)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = (
        select(Survey)
        .order_by(Survey.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total


async def get_survey(db: AsyncSession, survey_id: UUID) -> Survey | None:
    """Get a single survey by ID."""
    stmt = select(Survey).where(Survey.id == survey_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_survey(db: AsyncSession, data: SurveyCreate) -> Survey:
    """Create a new survey."""
    survey = Survey(**data.model_dump())
    db.add(survey)
    await db.flush()
    await db.refresh(survey)
    return survey


async def update_survey(
    db: AsyncSession,
    survey: Survey,
    data: SurveyUpdate,
) -> Survey:
    """Update an existing survey."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(survey, key, value)
    await db.flush()
    await db.refresh(survey)
    return survey


async def delete_survey(db: AsyncSession, survey: Survey) -> None:
    """Delete a survey."""
    await db.delete(survey)
    await db.flush()
