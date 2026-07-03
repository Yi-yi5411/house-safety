"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    ai_text,
    auth,
    component_templates,
    components,
    evaluation_standard_knowledge,
    evaluation_standards,
    original_records,
    report_signatures,
    report_templates,
    reports,
    structural_test_results,
    surveys,
    test_images,
    upload,
    users,
)

api_router = APIRouter(prefix="/v1")

# Auth & Users
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Core business
api_router.include_router(surveys.router, prefix="/surveys", tags=["surveys"])
api_router.include_router(components.router, prefix="/components", tags=["components"])
api_router.include_router(
    evaluation_standards.router, prefix="/evaluation-standards", tags=["evaluation-standards"]
)
api_router.include_router(
    component_templates.router, prefix="/component-templates", tags=["component-templates"]
)
api_router.include_router(
    evaluation_standard_knowledge.router,
    prefix="/evaluation-standard-knowledge",
    tags=["evaluation-standard-knowledge"],
)

# Report-related
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(
    original_records.router, prefix="/original-records", tags=["original-records"]
)
api_router.include_router(
    report_templates.router, prefix="/report-templates", tags=["report-templates"]
)
api_router.include_router(
    report_signatures.router,
    prefix="/surveys",
    tags=["signatures"],
)
api_router.include_router(
    structural_test_results.router,
    prefix="/surveys",
    tags=["structural-test-results"],
)
api_router.include_router(
    test_images.router,
    prefix="/surveys",
    tags=["test-images"],
)

# AI & Upload
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_text.router, prefix="/ai/text", tags=["ai-text"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
