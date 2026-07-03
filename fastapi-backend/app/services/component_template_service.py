"""CRUD operations for ComponentTemplate model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.component_template import ComponentTemplate
from app.schemas.component_template import (
    ComponentTemplateCreate,
    ComponentTemplateUpdate,
)


async def get_all_templates(db: AsyncSession) -> list[ComponentTemplate]:
    """Get all component templates ordered by display_order."""
    stmt = select(ComponentTemplate).order_by(ComponentTemplate.display_order)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: UUID) -> ComponentTemplate | None:
    """Get a single template by ID."""
    stmt = select(ComponentTemplate).where(ComponentTemplate.id == template_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_template(
    db: AsyncSession,
    data: ComponentTemplateCreate,
) -> ComponentTemplate:
    """Create a new component template."""
    template = ComponentTemplate(**data.model_dump())
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


async def update_template(
    db: AsyncSession,
    template: ComponentTemplate,
    data: ComponentTemplateUpdate,
) -> ComponentTemplate:
    """Update an existing component template."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    await db.flush()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template: ComponentTemplate) -> None:
    """Delete a component template."""
    await db.delete(template)
    await db.flush()
