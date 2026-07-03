"""CRUD operations for EvaluationStandardKnowledge model."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_standard_knowledge import EvaluationStandardKnowledge
from app.schemas.evaluation_standard_knowledge import (
    EvaluationStandardKnowledgeCreate,
    EvaluationStandardKnowledgeUpdate,
)


async def get_all_knowledge(db: AsyncSession) -> list[EvaluationStandardKnowledge]:
    """Get all knowledge entries."""
    stmt = select(EvaluationStandardKnowledge).order_by(
        EvaluationStandardKnowledge.type,
        EvaluationStandardKnowledge.name,
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_knowledge(
    db: AsyncSession,
    knowledge_id: uuid.UUID,
) -> EvaluationStandardKnowledge | None:
    """Get a single knowledge entry by ID."""
    stmt = select(EvaluationStandardKnowledge).where(
        EvaluationStandardKnowledge.id == knowledge_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_knowledge(
    db: AsyncSession,
    data: EvaluationStandardKnowledgeCreate,
) -> EvaluationStandardKnowledge:
    """Create a new knowledge entry."""
    knowledge = EvaluationStandardKnowledge(**data.model_dump())
    db.add(knowledge)
    await db.flush()
    await db.refresh(knowledge)
    return knowledge


async def update_knowledge(
    db: AsyncSession,
    knowledge: EvaluationStandardKnowledge,
    data: EvaluationStandardKnowledgeUpdate,
) -> EvaluationStandardKnowledge:
    """Update an existing knowledge entry."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(knowledge, key, value)
    await db.flush()
    await db.refresh(knowledge)
    return knowledge


async def delete_knowledge(
    db: AsyncSession,
    knowledge: EvaluationStandardKnowledge,
) -> None:
    """Delete a knowledge entry."""
    await db.delete(knowledge)
    await db.flush()
