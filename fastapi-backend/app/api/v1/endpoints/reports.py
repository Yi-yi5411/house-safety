"""Report and original record API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.component_check import ComponentCheck
from app.models.report_signature import ReportSignature
from app.models.structural_test_result import StructuralTestResult
from app.models.survey import Survey
from app.models.test_image import TestImage
from app.schemas.survey import SurveyResponse
from app.services.report_service import generate_report_docx, get_full_report_data
from app.services.original_record_service import (
    generate_original_record_docx,
    get_original_record_data,
)
from app.services.pdf_service import generate_report_pdf

router = APIRouter()


# ---- Report endpoints ----


@router.get("/{survey_id}")
async def get_report(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get report by survey ID — returns structured report content.

    Matches the old GET api/reports/:id behavior.
    """
    # Fetch survey
    result = await db.execute(
        select(Survey).where(Survey.id == survey_id, Survey.is_deleted == False)
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")

    # Fetch component checks
    comp_result = await db.execute(
        select(ComponentCheck).where(ComponentCheck.survey_id == survey_id)
    )
    components = comp_result.scalars().all()

    # Build survey info
    survey_info = {
        "id": str(survey.id),
        "address": survey.address,
        "buildYear": survey.build_year,
        "structureType": survey.structure_type,
        "floorCount": survey.floor_count,
        "buildArea": float(survey.build_area) if survey.build_area else None,
        "surveyTime": survey.survey_time.isoformat() if survey.survey_time else None,
        "conclusion": survey.conclusion,
        "basicEvaluation": survey.basic_evaluation,
        "aiReasoningResult": survey.ai_reasoning_result,
        "status": survey.status,
        "buildingProfile": survey.building_profile,
        "surveyNo": survey.survey_no,
        "surveyCategory": survey.survey_category,
        "surveyCategoryDesc": survey.survey_category_desc,
        "surveyPurpose": survey.survey_purpose,
        "sitePlanUrl": survey.site_plan_url,
        "reportData": survey.report_data,
        "createdAt": survey.created_at.isoformat() if survey.created_at else None,
    }

    # Build component checks list
    component_list = []
    for c in components:
        component_list.append({
            "id": str(c.id),
            "surveyId": str(c.survey_id),
            "name": c.name,
            "category": c.category,
            "axisLine": c.axis_line,
            "checkedItemIds": c.checked_item_ids or [],
            "aiEvaluationResult": c.ai_evaluation_result,
            "aiEvaluationClause": c.ai_evaluation_clause,
            "photos": c.photos or [],
            "damageLevel": c.damage_level,
            "damageDescription": c.damage_description,
        })

    return {
        "id": str(survey.id),
        "surveyId": str(survey.id),
        "content": {
            "title": f"房屋安全鉴定报告 - {survey.address}",
            "surveyInfo": survey_info,
            "componentChecks": component_list,
            "conclusion": survey.conclusion or "",
            "evaluation": survey.basic_evaluation or "",
        },
        "createdAt": survey.created_at.isoformat() if survey.created_at else None,
    }


@router.get("/{survey_id}/full-data")
async def get_report_full_data(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get complete report data for a survey (survey + checks + test results + signatures)."""
    return await get_full_report_data(survey_id, db)


@router.get("/{survey_id}/export")
async def export_report(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export the report as a .docx Word document."""
    docx_bytes = await generate_report_docx(survey_id, db)
    return StreamingResponse(
        docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=report-{survey_id}.docx"
        },
    )


@router.get("/{survey_id}/export/pdf")
async def export_report_pdf(
    survey_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export the report as a PDF document."""
    pdf_bytes = await generate_report_pdf(survey_id, db)
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report-{survey_id}.pdf"
        },
    )
