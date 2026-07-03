"""AI text generation API endpoints.

Ported from old AiTextGenerationService and ai-plugin.ts —
generates descriptive text for report sections.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.utils.ollama_client import (
    generate_cause_analysis,
    generate_conclusion,
    generate_damage_summary,
    generate_evaluation_standards,
    generate_external_environment,
    generate_handling_suggestion,
    generate_main_test_content,
    generate_safety_level,
    generate_structure_condition,
    generate_test_results,
    generate_test_standards,
    generate_usage_history,
)

router = APIRouter()


# ---- Original 4 endpoints ----


@router.post("/usage-history")
async def ai_usage_history(payload: dict) -> dict:
    """Generate usage history text."""
    text = await generate_usage_history(
        history_change=str(payload.get("historyChange", "")),
        usage_status=str(payload.get("usageStatus", "")),
        purpose_info=str(payload.get("purposeInfo", "")),
    )
    return {"content": text}


@router.post("/external-environment")
async def ai_external_environment(payload: dict) -> dict:
    """Generate external environment description."""
    text = await generate_external_environment(
        surrounding_environment=str(payload.get("surroundingEnvironment", "")),
        surrounding_environment_desc=str(payload.get("surroundingEnvironmentDesc", "")),
    )
    return {"content": text}


@router.post("/structure-condition")
async def ai_structure_condition(payload: dict) -> dict:
    """Generate structure condition description."""
    text = await generate_structure_condition(
        structure_info=str(payload.get("structureInfo", "")),
        basic_info=str(payload.get("basicInfo", "")),
    )
    return {"content": text}


@router.post("/evaluation-standards")
async def ai_evaluation_standards(payload: dict) -> dict:
    """Generate evaluation standards text."""
    text = await generate_evaluation_standards(
        building_info=str(payload.get("buildingInfo", "")),
    )
    return {"content": text}


@router.post("/remarks")
async def ai_remarks() -> dict:
    """Generate remarks text (returns standard text)."""
    return {
        "content": (
            "1、本鉴定书仅作为房屋安全性评估、房屋维护和危房治理的依据，不作他用；\n"
            "2、房屋需要进行维修、加固、重建的，应当到相关部门办理有关手续；\n"
            "3、本鉴定书中房屋建筑面积仅作为房屋鉴定收费依据，"
            "具体应以产权管理部门核定的建筑面积为准。"
        )
    }


# ---- New specialized generation endpoints (9 functions) ----


@router.post("/damage-summary")
async def ai_damage_summary(payload: dict) -> dict:
    """Generate damage summary based on building profile and component checks."""
    text = await generate_damage_summary(
        building_profile=payload.get("buildingProfile"),
        component_checks=payload.get("componentChecks"),
    )
    return {"content": text}


@router.post("/cause-analysis")
async def ai_cause_analysis(payload: dict) -> dict:
    """Generate cause analysis based on building profile and component checks."""
    text = await generate_cause_analysis(
        building_profile=payload.get("buildingProfile"),
        component_checks=payload.get("componentChecks"),
    )
    return {"content": text}


@router.post("/conclusion")
async def ai_conclusion(payload: dict) -> dict:
    """Generate assessment conclusion."""
    text = await generate_conclusion(
        building_profile=payload.get("buildingProfile"),
        component_checks=payload.get("componentChecks"),
    )
    return {"content": text}


@router.post("/handling-suggestion")
async def ai_handling_suggestion(payload: dict) -> dict:
    """Generate handling suggestions."""
    text = await generate_handling_suggestion(
        building_profile=payload.get("buildingProfile"),
        component_checks=payload.get("componentChecks"),
    )
    return {"content": text}


@router.post("/safety-level")
async def ai_safety_level(payload: dict) -> dict:
    """Determine safety level (A/B/C/D)."""
    text = await generate_safety_level(
        building_profile=payload.get("buildingProfile"),
        component_checks=payload.get("componentChecks"),
    )
    return {"content": text}


@router.post("/main-test-content")
async def ai_main_test_content(payload: dict) -> dict:
    """Generate main test content description."""
    text = await generate_main_test_content(
        building_profile=payload.get("buildingProfile"),
    )
    return {"content": text}


@router.post("/test-standards")
async def ai_test_standards(payload: dict) -> dict:
    """Generate applicable testing standards."""
    text = await generate_test_standards(
        main_test_content=payload.get("mainTestContent", ""),
    )
    return {"content": text}


@router.post("/test-results")
async def ai_test_results(payload: dict) -> dict:
    """Generate test results summary."""
    text = await generate_test_results(
        building_profile=payload.get("buildingProfile"),
        main_test_content=payload.get("mainTestContent", ""),
        test_standards=payload.get("testStandards", ""),
        component_checks=payload.get("componentChecks"),
    )
    return {"content": text}


