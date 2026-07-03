"""AI reasoning and assistant API endpoints."""

from __future__ import annotations

import json
import uuid
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user
from app.core.exceptions import NotFoundError
from app.db.database import get_db
from app.models.survey import Survey
from app.models.user import User
from app.schemas.common import AIReasonRequest, AIReasonResponse
from app.utils.ollama_client import generate_chat_completion, generate_structural_test_reasoning, stream_completion

router = APIRouter()

# In-memory conversation store (in production, use Redis)
_conversations: dict[str, list[dict[str, str]]] = {}


@router.post("/reason", response_model=AIReasonResponse)
async def ai_reason(
    payload: AIReasonRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AIReasonResponse:
    """Run AI reasoning on a survey and return structured results."""
    survey_id = uuid.UUID(payload.survey_id)
    result = await db.execute(
        select(Survey).where(
            Survey.id == survey_id, Survey.is_deleted == False
        )
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")

    # Load component checks for context
    from app.models.component_check import ComponentCheck

    comp_result = await db.execute(
        select(ComponentCheck).where(
            ComponentCheck.survey_id == survey_id
        )
    )
    components = comp_result.scalars().all()

    system_prompt = (
        "你是一名专业的房屋安全鉴定工程师。请根据房屋概况和构件检查数据，"
        "推理出鉴定结论（A/B/C/D级）、基础评定、风险等级和处置建议。"
        "请以JSON格式返回，包含字段: conclusion, basic_evaluation, risk_level, suggestion。"
    )

    survey_info = {
        "address": survey.address,
        "structure_type": survey.structure_type,
        "build_year": survey.build_year,
        "floor_count": survey.floor_count,
        "build_area": str(survey.build_area) if survey.build_area else None,
        "usage": survey.usage,
    }
    component_list = [
        {
            "name": c.name,
            "category": c.category,
            "damage_level": c.damage_level,
            "damage_description": c.damage_description,
        }
        for c in components
    ]

    user_prompt = payload.prompt or (
        f"房屋概况: {json.dumps(survey_info, ensure_ascii=False)}\n"
        f"构件检查: {json.dumps(component_list, ensure_ascii=False)}\n"
        "请给出鉴定结论和评定意见。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    raw_output = await generate_chat_completion(messages)

    # Try to parse JSON from the output
    reasoning_result = AIReasonResponse(raw_output=raw_output)
    try:
        # Extract JSON block if wrapped in markdown code fences
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        parsed = json.loads(cleaned)
        reasoning_result.conclusion = parsed.get("conclusion")
        reasoning_result.basic_evaluation = parsed.get("basic_evaluation")
        reasoning_result.risk_level = parsed.get("risk_level")
        reasoning_result.suggestion = parsed.get("suggestion")
    except (json.JSONDecodeError, AttributeError):
        pass

    # Persist to survey
    survey.conclusion = reasoning_result.conclusion
    survey.basic_evaluation = reasoning_result.basic_evaluation
    survey.risk_level = reasoning_result.risk_level
    survey.suggestion = reasoning_result.suggestion
    survey.ai_reasoning_result = {
        "conclusion": reasoning_result.conclusion,
        "basic_evaluation": reasoning_result.basic_evaluation,
        "risk_level": reasoning_result.risk_level,
        "suggestion": reasoning_result.suggestion,
        "raw_output": raw_output,
    }
    await db.flush()

    return reasoning_result


@router.post("/reason/stream")
async def ai_reason_stream(
    payload: AIReasonRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    """Stream AI reasoning output token by token."""
    survey_id = uuid.UUID(payload.survey_id)
    result = await db.execute(
        select(Survey).where(
            Survey.id == survey_id, Survey.is_deleted == False
        )
    )
    survey = result.scalar_one_or_none()
    if survey is None:
        raise NotFoundError(detail="Survey not found")

    system_prompt = (
        "你是一名专业的房屋安全鉴定工程师。请根据房屋概况和构件检查数据，"
        "推理出鉴定结论（A/B/C/D级）、基础评定、风险等级和处置建议。"
    )

    user_prompt = payload.prompt or "请给出鉴定结论和评定意见。"

    async def generate() -> AsyncGenerator[str, None]:
        async for token in stream_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
        ):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")


# ---- AI Report Modification Assistant (Chat) ----


@router.post("/assistant/chat")
async def ai_assistant_chat(payload: dict) -> dict:
    """Chat with the AI report modification assistant (non-streaming).

    Payload:
      - conversation_id: str (optional, for multi-turn conversation)
      - message: str (user's question)
      - report_content: str (report context)
      - survey_id: str (optional, for loading survey context)
    """
    conversation_id = payload.get("conversation_id") or str(uuid.uuid4())
    user_message = payload.get("message", "")
    report_content = payload.get("report_content", "")

    # Initialize or load conversation
    if conversation_id not in _conversations:
        system_prompt = (
            "你是一名专业的房屋安全鉴定报告修改助手。你的任务是帮助用户修改和完善房屋安全鉴定报告。"
            "你可以根据用户的提问，生成报告修改建议。"
            "请基于以下报告内容进行回答：\n\n"
            f"{report_content[:3000]}\n\n"
            "请用专业、准确的语言回答用户的问题。"
        )
        _conversations[conversation_id] = [
            {"role": "system", "content": system_prompt}
        ]

    _conversations[conversation_id].append({"role": "user", "content": user_message})

    # Truncate history to prevent overflow
    if len(_conversations[conversation_id]) > 20:
        _conversations[conversation_id] = [
            _conversations[conversation_id][0]  # Keep system prompt
        ] + _conversations[conversation_id][-19:]

    response = await generate_chat_completion(
        _conversations[conversation_id],
        temperature=0.5,
        max_tokens=2048,
    )

    _conversations[conversation_id].append({"role": "assistant", "content": response})

    return {
        "conversation_id": conversation_id,
        "content": response,
    }


@router.post("/assistant/chat/stream")
async def ai_assistant_chat_stream(payload: dict) -> StreamingResponse:
    """Chat with the AI report modification assistant (SSE streaming).

    Payload:
      - conversation_id: str (optional)
      - message: str (user's question)
      - report_content: str (report context)
    """
    conversation_id = payload.get("conversation_id") or str(uuid.uuid4())
    user_message = payload.get("message", "")
    report_content = payload.get("report_content", "")

    # Initialize or load conversation
    if conversation_id not in _conversations:
        system_prompt = (
            "你是一名专业的房屋安全鉴定报告修改助手。你的任务是帮助用户修改和完善房屋安全鉴定报告。"
            "你可以根据用户的提问，生成报告修改建议。"
            "请基于以下报告内容进行回答：\n\n"
            f"{report_content[:3000]}\n\n"
            "请用专业、准确的语言回答用户的问题。"
        )
        _conversations[conversation_id] = [
            {"role": "system", "content": system_prompt}
        ]

    _conversations[conversation_id].append({"role": "user", "content": user_message})

    # Build prompt from conversation history for stream_completion
    history_text = "\n".join(
        f"{'用户' if m['role'] == 'user' else '助手' if m['role'] == 'assistant' else '系统'}: {m['content']}"
        for m in _conversations[conversation_id]
    )

    async def generate() -> AsyncGenerator[str, None]:
        full_response = ""
        async for token in stream_completion(
            prompt=history_text,
            system_prompt=(
                "你是一名专业的房屋安全鉴定报告修改助手。用专业、准确的中文回答。"
            ),
            temperature=0.5,
        ):
            full_response += token
            yield f"data: {json.dumps({'token': token, 'conversation_id': conversation_id})}\n\n"

        # Save assistant response to conversation history
        if conversation_id in _conversations:
            _conversations[conversation_id].append(
                {"role": "assistant", "content": full_response}
            )
            # Truncate
            if len(_conversations[conversation_id]) > 20:
                _conversations[conversation_id] = [
                    _conversations[conversation_id][0]
                ] + _conversations[conversation_id][-19:]

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/assistant/clear")
async def ai_assistant_clear(payload: dict) -> dict:
    """Clear a conversation history."""
    conversation_id = payload.get("conversation_id")
    if conversation_id and conversation_id in _conversations:
        del _conversations[conversation_id]
        return {"status": "cleared", "conversation_id": conversation_id}
    return {"status": "not_found"}


@router.get("/assistant/conversations")
async def ai_assistant_list_conversations() -> dict:
    """List active conversation IDs (for debugging)."""
    return {"conversations": list(_conversations.keys())}


@router.post("/structural-reason")
async def ai_structural_reason(payload: dict) -> dict:
    """AI推理生成完整的结构检测结果。

    根据房屋概况和构件检查数据，一次性生成:
    主要检测内容、检测依据标准、主要检测成果、
    损坏情况综述、原因分析、鉴定结论、处理意见、安全等级。

    Payload:
      - building_profile: dict (房屋概况)
      - component_checks: list[dict] (构件检查记录)
    """
    result = await generate_structural_test_reasoning(
        building_profile=payload.get("building_profile"),
        component_checks=payload.get("component_checks"),
    )
    return result
