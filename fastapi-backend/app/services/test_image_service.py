"""CRUD operations for TestImage model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_image import TestImage
from app.schemas.test_image import TestImageCreate, TestImageUpdate


async def get_images_by_survey(
    db: AsyncSession,
    survey_id: UUID,
) -> list[TestImage]:
    """Get all test images for a survey."""
    stmt = (
        select(TestImage)
        .where(TestImage.survey_id == survey_id)
        .order_by(TestImage.sort_order, TestImage.created_at)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_image(db: AsyncSession, image_id: UUID) -> TestImage | None:
    """Get a single test image by ID."""
    stmt = select(TestImage).where(TestImage.id == image_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_image(db: AsyncSession, data: TestImageCreate) -> TestImage:
    """Create a new test image."""
    image = TestImage(**data.model_dump())
    db.add(image)
    await db.flush()
    await db.refresh(image)
    return image


async def update_image(
    db: AsyncSession,
    image: TestImage,
    data: TestImageUpdate,
) -> TestImage:
    """Update an existing test image."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(image, key, value)
    await db.flush()
    await db.refresh(image)
    return image


async def delete_image(db: AsyncSession, image: TestImage) -> None:
    """Delete a test image."""
    await db.delete(image)
    await db.flush()
