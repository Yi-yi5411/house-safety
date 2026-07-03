"""Evaluation Standard Knowledge API endpoints (鉴定依据标准知识库)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.evaluation_standard_knowledge import (
    EvaluationStandardKnowledgeCreate,
    EvaluationStandardKnowledgeListResponse,
    EvaluationStandardKnowledgeResponse,
    EvaluationStandardKnowledgeUpdate,
)
from app.services import evaluation_standard_knowledge_service as service

router = APIRouter()


@router.get("/", response_model=EvaluationStandardKnowledgeListResponse)
async def list_knowledge_entries(
    db: AsyncSession = Depends(get_db),
) -> EvaluationStandardKnowledgeListResponse:
    """List all evaluation standard knowledge entries (鉴定依据标准知识库列表)."""
    items = await service.get_all_knowledge(db)
    return EvaluationStandardKnowledgeListResponse(
        items=[EvaluationStandardKnowledgeResponse.model_validate(item) for item in items]
    )


@router.get("/{knowledge_id}", response_model=EvaluationStandardKnowledgeResponse)
async def get_knowledge_entry(
    knowledge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> EvaluationStandardKnowledgeResponse:
    """Get a single evaluation standard knowledge entry by ID."""
    entry = await service.get_knowledge(db, knowledge_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库条目不存在")
    return EvaluationStandardKnowledgeResponse.model_validate(entry)


@router.post(
    "/",
    response_model=EvaluationStandardKnowledgeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_entry(
    data: EvaluationStandardKnowledgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationStandardKnowledgeResponse:
    """Create a new evaluation standard knowledge entry."""
    entry = await service.create_knowledge(db, data)
    return EvaluationStandardKnowledgeResponse.model_validate(entry)


@router.put("/{knowledge_id}", response_model=EvaluationStandardKnowledgeResponse)
async def update_knowledge_entry(
    knowledge_id: uuid.UUID,
    data: EvaluationStandardKnowledgeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationStandardKnowledgeResponse:
    """Update an existing evaluation standard knowledge entry."""
    entry = await service.get_knowledge(db, knowledge_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库条目不存在")
    updated = await service.update_knowledge(db, entry, data)
    return EvaluationStandardKnowledgeResponse.model_validate(updated)


@router.delete("/{knowledge_id}")
async def delete_knowledge_entry(
    knowledge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an evaluation standard knowledge entry."""
    entry = await service.get_knowledge(db, knowledge_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库条目不存在")
    await service.delete_knowledge(db, entry)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
