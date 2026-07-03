"""Original record API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.original_record_service import (
    generate_original_record_docx,
    get_original_record_data,
)
from app.services.pdf_service import generate_original_record_pdf

router = APIRouter()


@router.get("/{survey_id}")
async def get_original_record(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get original record data for a survey."""
    return await get_original_record_data(survey_id, db)


@router.get("/{survey_id}/export")
async def export_original_record(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export the original record as a .docx Word document."""
    docx_bytes = await generate_original_record_docx(survey_id, db)
    return StreamingResponse(
        docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=original-record-{survey_id}.docx"
        },
    )


@router.get("/{survey_id}/export/pdf")
async def export_original_record_pdf(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export the original record as a PDF document."""
    pdf_bytes = await generate_original_record_pdf(survey_id, db)
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=original-record-{survey_id}.pdf"
        },
    )
