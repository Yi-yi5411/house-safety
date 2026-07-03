"""Test image API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.test_image import TestImage
from app.models.user import User
from app.schemas.test_image import (
    TestImageCreate,
    TestImageListResponse,
    TestImageReorderRequest,
    TestImageResponse,
    TestImageUpdate,
)

router = APIRouter()


@router.get("/{survey_id}/test-images", response_model=TestImageListResponse)
async def list_test_images(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TestImageListResponse:
    """List test images for a survey, ordered by sort_order."""
    result = await db.execute(
        select(TestImage)
        .where(TestImage.survey_id == survey_id)
        .order_by(TestImage.sort_order)
    )
    items = result.scalars().all()
    return TestImageListResponse(
        items=[TestImageResponse.model_validate(img) for img in items],
        total=len(items),
    )


@router.post(
    "/{survey_id}/test-images",
    response_model=TestImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_image(
    survey_id: uuid.UUID,
    payload: TestImageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestImage:
    """Create a new test image record."""
    img = TestImage(survey_id=survey_id, **payload.model_dump())
    db.add(img)
    await db.flush()
    await db.refresh(img)
    return img


@router.put("/{survey_id}/test-images/{image_id}", response_model=TestImageResponse)
async def update_test_image(
    survey_id: uuid.UUID,
    image_id: uuid.UUID,
    payload: TestImageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestImage:
    """Update a test image."""
    result = await db.execute(
        select(TestImage).where(
            TestImage.id == image_id,
            TestImage.survey_id == survey_id,
        )
    )
    img = result.scalar_one_or_none()
    if img is None:
        raise NotFoundError(detail="Test image not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(img, field, value)
    await db.flush()
    await db.refresh(img)
    return img


@router.put("/{survey_id}/test-images/reorder")
async def reorder_test_images(
    survey_id: uuid.UUID,
    payload: TestImageReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Batch reorder test images for a survey."""
    for item in payload.items:
        await db.execute(
            update(TestImage)
            .where(TestImage.id == item.id, TestImage.survey_id == survey_id)
            .values(sort_order=item.sort_order)
        )
    await db.flush()
    return {"message": "ok"}


@router.delete("/{survey_id}/test-images/{image_id}")
async def delete_test_image(
    survey_id: uuid.UUID,
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a test image."""
    result = await db.execute(
        select(TestImage).where(
            TestImage.id == image_id,
            TestImage.survey_id == survey_id,
        )
    )
    img = result.scalar_one_or_none()
    if img is None:
        raise NotFoundError(detail="Test image not found")
    await db.delete(img)
    await db.flush()
