# -*- coding: utf-8 -*-
"""
Ollama 大语言模型客户端封装 (Ollama LLM Client Wrapper).
========================================================
本模块封装了与 Ollama 本地大模型的所有交互，为 uniapp 小程序提供 AI 文本生成能力：

- 数据采集页 (data-collection.vue)：
  使用历史、外部环境、结构状况、鉴定依据标准

- 构件检查/结构检测页 (structural-test.vue)：
  损坏情况综述、损坏原因分析、鉴定结论

- 检测结果推理页 (test-result-inference.vue)：
  主要检测内容、检测依据标准、主要检测成果、
  损坏情况综述、原因分析、鉴定结论、处理意见、安全等级

- 结构检测推理 (ai.py /ai/structural-reason)：
  一次性生成完整结构检测结果的所有字段

==== 提示词设计模式 (Prompt Design Pattern) ====

  Layer 1 — system_prompt: 角色设定 + 中文输出约束
  Layer 2 — user_prompt: 任务描述 + 输出规则 + 输入数据 + 最终指令
  Layer 3 — generate_chat_completion(temperature=0.1~0.3, max_tokens=1024~4096)

==== 重要配置 ====
- think=False: 禁用 qwen3 模型的"思考模式"
- timeout=300s: 本地模型推理较慢，需足够超时时间
"""

from __future__ import annotations

from typing import Any, AsyncGenerator

import httpx
from loguru import logger

from app.core.config import get_settings


# ============================================================================
# 第一层：核心 API 封装 (Core API Wrappers)
# ============================================================================
# 以下三个函数是本模块的基础设施，所有上层的生成函数最终都调用它们。
# 对应 Ollama 的两个 REST API 端点：/api/generate 和 /api/chat
# ============================================================================


async def generate_completion(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
) -> str:
    """调用 Ollama /api/generate 端点，生成单次文本补全。

    适用场景：简单的单轮文本生成，不需要多轮对话上下文。
    对应 Ollama 的 Completion API（非 Chat API）。

    Args:
        prompt: 用户输入的提示文本。
        system_prompt: 可选的系统提示，用于设定模型角色和行为。
        temperature: 采样温度，越高越随机（0~1）。报告生成建议 0.1~0.3。
        max_tokens: 最大生成 token 数。qwen3 思考模式需较大值，但已通过 think=False 禁用。

    Returns:
        模型生成的文本字符串。如果响应为空且存在 thinking 内容，则回退使用 thinking。
    """
    # 获取应用配置，包含 Ollama 服务地址和模型名称
    settings = get_settings()
    # 拼接 Ollama 的 /api/generate 端点 URL
    url = f"{settings.ollama_base_url}/api/generate"

    # 构建请求体参数
    payload: dict[str, Any] = {
        "model": settings.ollama_model,        # 指定使用的模型名称（如 qwen3:7b）
        "prompt": prompt,                      # 用户输入的提示文本
        "stream": False,                       # 非流式输出，等待完整结果后返回
        "options": {
            "temperature": temperature,        # 采样温度，低温度保证输出稳定
            "num_predict": max_tokens,         # 最大生成 token 数
        },
    }
    # 如果提供了系统提示，则添加到请求中
    if system_prompt:
        payload["system"] = system_prompt
    # 关键配置：禁用 qwen3 模型的"思考模式"，否则所有 token 被内部推理消耗，实际回复为空
    payload["think"] = False

    # 发送 HTTP 请求到 Ollama 服务
    try:
        # 创建异步 HTTP 客户端，设置超时时间为 300 秒（本地模型推理较慢）
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            output = result.get("response", "")
            if not output and result.get("thinking"):
                logger.info("Ollama: response empty, using thinking content")
                output = result.get("thinking", "")
            if not output:
                logger.warning(
                    f"Ollama returned empty response (eval_count={result.get('eval_count')}, "
                    f"thinking_len={len(result.get('thinking', ''))})"
                )
            logger.info(f"Ollama generation completed, length={len(output)}")
            return output
    except httpx.HTTPError as exc:
        # 捕获 HTTP 错误，记录日志并重新抛出
        logger.error(f"Ollama generation failed: {exc}")
        raise


async def generate_chat_completion(
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 8192,
) -> str:
    """调用 Ollama /api/chat 端点，生成多轮对话式文本补全。

    适用场景：需要多轮对话上下文的文本生成，支持 system/user/assistant 三种角色消息。
    对应 Ollama 的 Chat Completion API。

    对于 qwen3 模型，如果 thinking 模式被意外激活，会将 thinking + response 内容合并返回。

    Args:
        messages: 消息列表，每个消息是包含 'role' 和 'content' 的字典。
                  支持角色：'system'（系统提示）、'user'（用户输入）、'assistant'（助手回复）。
        temperature: 采样温度，越高越随机（0~1）。报告生成建议 0.1~0.3。
        max_tokens: 最大生成 token 数。

    Returns:
        模型生成的文本字符串。
    """
    # 获取应用配置，包含 Ollama 服务地址和模型名称
    settings = get_settings()
    # 拼接 Ollama 的 /api/chat 端点 URL
    url = f"{settings.ollama_base_url}/api/chat"

    # 构建请求体参数
    payload: dict[str, Any] = {
        "model": settings.ollama_model,        # 指定使用的模型名称
        "messages": messages,                  # 对话消息列表（包含上下文历史）
        "stream": False,                       # 非流式输出
        "options": {
            "temperature": temperature,        # 采样温度
            "num_predict": max_tokens,         # 最大生成 token 数
        },
    }
    # 关键配置：禁用 qwen3 模型的"思考模式"
    payload["think"] = False

    # 发送 HTTP 请求到 Ollama 服务
    try:
        async with httpx.AsyncClient(timeout=300.0, ) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            # 从响应中提取 message 对象
            message = result.get("message", {})
            # 提取 message 中的 content 字段（模型生成的回复内容）
            output = message.get("content", "")
            # 回退机制：如果 think=False 不被支持，使用 thinking 内容
            if not output and result.get("thinking"):
                logger.info("Ollama chat: response empty, using thinking content")
                output = result.get("thinking", "")
            # 日志记录：如果输出为空，记录警告信息
            if not output:
                logger.warning(
                    f"Ollama chat returned empty (eval_count={result.get('eval_count')})"
                )
            # 日志记录：生成完成，记录输出长度
            logger.info(f"Ollama chat generation completed, length={len(output)}")
            return output
    except httpx.HTTPError as exc:
        # 捕获 HTTP 错误，记录日志并重新抛出
        logger.error(f"Ollama chat generation failed: {exc}")
        raise


async def stream_completion(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """调用 Ollama /api/generate 端点，流式生成文本补全（逐 token 返回）。

    适用场景：需要实时展示生成进度的场景，如 AI 助手对话、长文本生成的进度展示。
    客户端可以在模型生成过程中逐字/逐句显示内容，提升用户体验。

    Args:
        prompt: 用户输入的提示文本。
        system_prompt: 可选的系统提示，用于设定模型角色和行为。
        temperature: 采样温度，越高越随机（0~1）。

    Yields:
        生成的文本片段（chunk），每次 yield 返回一个或多个 token。
    """
    # 获取应用配置，包含 Ollama 服务地址和模型名称
    settings = get_settings()
    # 拼接 Ollama 的 /api/generate 端点 URL
    url = f"{settings.ollama_base_url}/api/generate"

    # 构建请求体参数
    payload: dict[str, Any] = {
        "model": settings.ollama_model,        # 指定使用的模型名称
        "prompt": prompt,                      # 用户输入的提示文本
        "stream": True,                        # 启用流式输出（关键配置）
        "options": {
            "temperature": temperature,        # 采样温度
            "num_predict": 8192,               # 最大生成 token 数
        },
    }
    # 如果提供了系统提示，则添加到请求中
    if system_prompt:
        payload["system"] = system_prompt
    # 关键配置：禁用 qwen3 模型的"思考模式"
    payload["think"] = False

    # 发送流式 HTTP 请求到 Ollama 服务
    try:
        async with httpx.AsyncClient(timeout=300.0, ) as client:
            # 使用 stream 方法发送 POST 请求，支持流式接收响应
            async with client.stream("POST", url, json=payload) as response:
                # 检查 HTTP 状态码
                response.raise_for_status()
                # 异步迭代响应的每一行（Ollama 流式输出每行是一个 JSON 对象）
                async for line in response.aiter_lines():
                    # 跳过空行
                    if not line:
                        continue
                    # 延迟导入 json 模块（避免模块加载开销）
                    import json as _json
                    # 解析每行的 JSON 数据
                    chunk = _json.loads(line)
                    # 提取当前生成的 token（response 字段）
                    token = chunk.get("response", "")
                    # 如果 think=False 不被支持且 response 为空，使用 thinking 内容避免流静默
                    if not token and chunk.get("thinking"):
                        token = chunk.get("thinking", "")
                    # 如果有 token，yield 给调用方
                    if token:
                        yield token
                    # 检查是否到达生成末尾（done 字段为 True）
                    if chunk.get("done"):
                        break
    except httpx.HTTPError as exc:
        # 捕获 HTTP 错误，记录日志并重新抛出
        logger.error(f"Ollama stream failed: {exc}")
        raise


# ---------------------------------------------------------------------------
# 第二层：数据采集页 AI 辅助生成函数 (Data Collection Page Helpers)
# ---------------------------------------------------------------------------
# 以下函数从旧的 AiTextGenerationService 迁移而来，为 uniapp 小程序数据采集页面提供 AI 辅助生成能力。
# 对应页面：data-collection.vue
# ---------------------------------------------------------------------------


async def generate_usage_history(
    history_change: str = "",
    usage_status: str = "",
    purpose_info: str = "",
) -> str:
    """生成报告中"房屋使用、维修、改造、灾害等历史情况"部分的描述文本。

    对应数据采集页面的"使用历史"字段。
    根据房屋的历史变更信息（用途变更、维修、加固、灾害）、使用状况和用途信息，
    自动生成符合报告规范的描述文本。

    Args:
        history_change: 历史变更信息（用途变更、维修、加固、灾害等情况）。
        usage_status: 使用状况信息（结构改动、违法建设、超载使用等情况）。
        purpose_info: 用途信息（原设计用途、现用途）。

    Returns:
        生成的使用历史描述文本（中文），控制在 150 字以内。
    """
    # 系统提示：设定模型角色为房屋安全鉴定报告撰写专家，强制中文输出
    system_prompt = (
        "你是一位房屋安全鉴定报告撰写专家。你必须始终使用中文输出。"
    )
    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        '你是一位房屋安全鉴定报告撰写专家。请根据以下房屋历史变更、使用情况和用途信息,'
        '生成"房屋使用、维修、改造、灾害等历史情况"的描述。\n\n'
        '输出规则(严格按以下规则生成):\n'
        '1. 对于历史变更信息中的每一项:\n'
        '   - 如果值为"无"或"no":输出"该房屋无XX历史"(如"该房屋无用途变更历史")\n'
        '   - 如果值为"有"或"yes":具体描述该项。例如用途变更需说明'
        '"该房屋用途发生了变更,原设计用途为xxx,现用途为xxx"\n'
        '   - 如果值为"不详"或"unknown":输出"该房屋XX情况不详"\n'
        '2. 对于使用情况信息同样按上述规则处理\n'
        '3. 输出控制在150字以内\n'
        '4. 只陈述事实,不展开分析\n'
        '5. 输出纯文本,不加标题或格式标记\n'
        '6. 必须使用中文输出\n\n'
        f'历史变更信息:\n{history_change or "无"}\n\n'
        f'使用情况信息:\n{usage_status or "无"}\n\n'
        f'用途信息:\n{purpose_info or "无"}\n\n'
        '请生成最终的使用历史描述:'
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_external_environment(
    surrounding_environment: str = "",
    surrounding_environment_desc: str = "",
) -> str:
    """生成报告中"房屋外部环境及周边建设施工情况"部分的描述文本。

    对应数据采集页面的"外部环境"字段。
    根据房屋周边环境类型（正常无施工、深基坑施工、其他）和详细描述，
    自动生成符合报告规范的外部环境描述。

    Args:
        surrounding_environment: 周边环境类型（如"正常无施工"、"深基坑施工"、"其他"）。
        surrounding_environment_desc: 周边环境详细描述。

    Returns:
        生成的外部环境描述文本（中文），控制在 100 字以内。
    """
    # 系统提示：设定模型角色为房屋安全鉴定报告撰写专家，强制中文输出
    system_prompt = (
        "你是一位房屋安全鉴定报告撰写专家。你必须始终使用中文输出。"
    )
    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        '你是一位房屋安全鉴定报告撰写专家。请根据以下房屋周边环境信息,'
        '生成"房屋外部环境及周边建设施工情况"的描述。\n\n'
        '输出规则:\n'
        '1. 如果周边环境为"不详"或"unknown":输出"该房屋周边环境情况不详"\n'
        '2. 如果周边环境为"正常无施工":输出"该房屋周边环境正常,周边无施工活动"\n'
        '3. 如果周边环境为"深基坑施工"或"其他":根据描述简要说明施工情况\n'
        '4. 输出控制在100字以内\n'
        '5. 输出纯文本,不加标题或格式标记\n'
        '6. 必须使用中文输出\n\n'
        f'周边环境类型:{surrounding_environment or "正常无施工"}\n'
        f'周边环境描述:{surrounding_environment_desc or "无"}\n\n'
        '请生成最终的外部环境描述:'
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_structure_condition(
    structure_info: str = "",
    basic_info: str = "",
) -> str:
    """生成报告中"房屋地质勘察、地基基础、主体结构及其他情况"部分的描述文本。

    对应数据采集页面的"结构状况"字段。
    根据房屋结构信息（结构类型、基础类型、墙体类型、楼盖类型等）和基本信息，
    按"地质勘察-地基基础-主体结构-其他"的顺序自动生成符合报告规范的结构状况描述。

    Args:
        structure_info: 结构信息（结构类型、基础类型、地基处理、墙体类型、楼盖类型等）。
        basic_info: 房屋基本信息（建筑面积、层数、层高、建成年份等）。

    Returns:
        生成的结构状况描述文本（中文），控制在 200 字以内。
    """
    # 系统提示：设定模型角色为房屋安全鉴定报告撰写专家，强制中文输出
    system_prompt = (
        "你是一位房屋安全鉴定报告撰写专家。你必须始终使用中文输出。"
    )
    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        '你是一位房屋安全鉴定报告撰写专家。请根据以下房屋结构信息,'
        '生成"房屋地质勘察、地基基础、主体结构及其他情况"的描述。\n\n'
        '输出规则:\n'
        '1. 对于值为"不详"或"unknown"的项:输出"XX情况不详"\n'
        '2. 对于有具体值的项:简要说明该结构要素的现状\n'
        '3. 按"地质勘察-地基基础-主体结构-其他"的顺序组织内容\n'
        '4. 输出控制在200字以内\n'
        '5. 输出纯文本,不加标题或格式标记\n'
        '6. 必须使用中文输出\n\n'
        f'结构信息:\n{structure_info or "不详"}\n\n'
        f'基本信息:\n{basic_info or "无"}\n\n'
        '请生成最终的结构状况描述:'
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_evaluation_standards(
    building_info: str = "",
) -> str:
    """生成报告中"鉴定依据标准"部分的描述文本。

    对应数据采集页面的"鉴定依据标准"字段。
    根据房屋基本信息，智能生成适用的鉴定标准列表。

    Args:
        building_info: 房屋基本信息描述。

    Returns:
        生成的鉴定依据标准文本（中文），格式为编号列表。
    """
    system_prompt = (
        "你是一位房屋安全鉴定报告撰写专家。你必须始终使用中文输出。"
    )
    user_prompt = (
        "你是一位房屋安全鉴定报告撰写专家。请根据以下房屋信息，"
        '生成"鉴定依据标准"的内容。\n\n'
        "输出规则:\n"
        "1. 格式:1、《规范名称》规范编号;2、《规范名称》规范编号\n"
        "2. 必须包含以下标准（根据房屋情况选择适用的）:\n"
        "   《危险房屋鉴定标准》JGJ 125-2016（必含）\n"
        "   《建筑结构检测技术标准》GB/T 50344-2019（必含）\n"
        "   《建筑变形测量规范》JGJ 8-2016\n"
        "   《房屋完损等级评定标准》（建设部城住字[84]第678号）\n"
        "   《建筑抗震鉴定标准》GB 50023-2009\n"
        "   《建筑结构荷载规范》GB 50009-2012\n"
        "   《砌体结构设计规范》GB 50003-2011\n"
        "   《混凝土结构设计规范》GB 50010-2010\n"
        "   《建筑地基基础设计规范》GB 50007-2011\n"
        "3. 根据房屋结构类型选择3-6个最相关的标准\n"
        "4. 语言规范、准确\n5. 必须使用中文输出\n\n"
        f"房屋信息:\n{building_info or '一般建筑结构'}\n\n"
        "请直接生成最终的鉴定依据标准文本:"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=1024)


async def generate_structural_test_reasoning(
    building_profile: dict | None = None,
    component_checks: list[dict] | None = None,
) -> dict[str, str]:
    """AI推理生成结构检测结果的所有字段。

    对应客户端的"检测结果推理"功能，一次性生成:
    - main_test_content: 主要检测内容
    - test_standards: 检测依据标准
    - test_results_summary: 主要检测成果
    - damage_summary: 损坏情况综述
    - cause_analysis: 原因分析
    - conclusion: 鉴定结论
    - handling_suggestion: 处理意见
    - safety_level: 安全等级 (A/B/C/D)
    """
    building_profile = building_profile or {}
    component_checks = component_checks or []

    comp_desc = "\n".join(
        f"- {c.get('name', '')} ({c.get('category', '')}): "
        f"损坏等级 {c.get('damage_level', 'N/A')}, "
        f"描述: {c.get('damage_description', 'N/A')}"
        for c in component_checks[:30]
    )

    system_prompt = (
        "你是一位专业的房屋安全鉴定工程师。你必须始终使用中文输出。"
        "请根据房屋概况和构件检查数据，生成完整的结构检测结果。"
        "你必须以JSON格式返回，包含以下字段: "
        "main_test_content (主要检测内容), test_standards (检测依据标准), "
        "test_results_summary (主要检测成果), damage_summary (损坏情况综述), "
        "cause_analysis (原因分析), conclusion (鉴定结论A/B/C/D级), "
        "handling_suggestion (处理意见), safety_level (安全等级: A/B/C/D)。"
    )

    user_prompt = (
        "你是一位专业的房屋安全鉴定工程师。请根据以下房屋概况信息和构件检查数据，"
        "生成完整的结构检测结果，并以JSON格式返回。\n\n"
        "输出规则:\n"
        "1. main_test_content: 主要检测内容描述，格式为编号列表 (1、XXXX;2、XXXX)\n"
        "2. test_standards: 检测依据标准列表，格式为编号列表，必须包含《危险房屋鉴定标准》JGJ 125-2016\n"
        "3. test_results_summary: 主要检测成果，包含外观质量检查和倾斜观测结果\n"
        "4. damage_summary: 房屋损坏情况综述，约200-400字\n"
        "5. cause_analysis: 损坏原因分析，约150-300字\n"
        "6. conclusion: 鉴定结论，包含各组成部分评定结果和整体安全性评定\n"
        "7. handling_suggestion: 处理意见，根据安全等级给出相应建议\n"
        "8. safety_level: 安全等级，只能是 A、B、C 或 D\n"
        "9. 所有字段必须使用中文输出\n"
        "10. 返回格式: {\"main_test_content\":\"...\",\"test_standards\":\"...\",...}\n\n"
        f"房屋概况信息:\n{building_profile}\n\n"
        f"构件检查数据:\n{comp_desc or '无'}\n\n"
        "请生成最终的JSON结果:"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    raw_output = await generate_chat_completion(messages, temperature=0.3, max_tokens=4096)

    # Parse JSON from output
    import json as _json
    try:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        result = _json.loads(cleaned)
        # Normalize: join arrays into strings with newlines or semicolons
        normalized = {}
        list_joiners = {
            "main_test_content": "\n",
            "test_standards": "\n",
            "test_results_summary": "\n",
        }
        for key, value in result.items():
            if isinstance(value, list):
                sep = list_joiners.get(key, "；")
                normalized[key] = sep.join(str(v) for v in value)
            else:
                normalized[key] = str(value) if value else ""
        return normalized
    except (_json.JSONDecodeError, AttributeError):
        return {"raw_output": raw_output}


# ---------------------------------------------------------------------------
# 鉴定报告/检测结果页 AI 生成函数
# ---------------------------------------------------------------------------
# 用于 structural-test.vue（构件检查页）、test-result-inference.vue（检测结果推理页）
# ---------------------------------------------------------------------------


async def generate_damage_summary(
    building_profile: dict = None,
    component_checks: list[dict] = None,
) -> str:
    """生成鉴定报告中"房屋损坏情况综述"部分的专业描述。

    对应鉴定报告页面的"损坏情况综述"字段。
    根据房屋概况信息和构件检查记录，全面、客观地概括房屋各部位的损坏状况，
    包括地基基础、上部承重结构、围护结构、楼地面、屋面、内外抹灰、门窗及设备等。

    Args:
        building_profile: 房屋概况信息字典（包含基本信息、结构信息等）。
        component_checks: 构件检查记录列表，每个记录包含构件名称、分类、损坏等级等。

    Returns:
        生成的房屋损坏情况综述文本（中文），约 200-400 字。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}
    component_checks = component_checks or []

    # 系统提示：设定模型角色为专业的房屋安全鉴定工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋安全鉴定工程师。你必须始终使用中文输出。"
    )

    # 将构件检查列表格式化为可读的文本描述（最多取前 30 条）
    comp_desc = "\n".join(
        f"- {c.get('name', '')} ({c.get('category', '')}): "
        f"损坏等级 {c.get('damage_level', 'N/A')}, "
        f"描述: {c.get('damage_description', 'N/A')}"
        for c in component_checks[:30]
    )

    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋安全鉴定工程师。请根据以下房屋信息和构件检查结果,"
        '生成"房屋损坏情况综述"的专业描述。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式鉴定报告的最终文本\n"
        "2. 内容应全面、客观地概括房屋的损坏状况,包括地基基础、上部承重结构、"
        "围护结构、楼地面、屋面、内外抹灰、门窗及设备的损坏情况\n"
        "3. 按照损坏程度进行归纳总结,突出主要问题\n"
        "4. 语言专业、客观、简洁,符合鉴定报告规范\n"
        "5. 篇幅适中,约200-400字\n"
        "6. 必须使用中文输出\n\n"
        f"房屋信息: {building_profile}\n"
        f"构件检查:\n{comp_desc}\n"
        "请生成最终的房屋损坏情况综述:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_cause_analysis(
    building_profile: dict = None,
    component_checks: list[dict] = None,
) -> str:
    """生成鉴定报告中"房屋损坏原因分析"部分的专业描述。

    对应鉴定报告页面的"损坏原因分析"字段。
    根据房屋概况信息和构件检查记录，分析房屋损坏的可能原因，
    包括材料老化、施工质量、使用荷载变化、环境因素、地基基础问题等。

    Args:
        building_profile: 房屋概况信息字典（包含基本信息、结构信息等）。
        component_checks: 构件检查记录列表，每个记录包含构件名称、分类、损坏等级等。

    Returns:
        生成的房屋损坏原因分析文本（中文），约 150-300 字。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}
    component_checks = component_checks or []

    # 系统提示：设定模型角色为专业的房屋安全鉴定工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋安全鉴定工程师。你必须始终使用中文输出。"
    )

    # 将构件检查列表格式化为可读的文本描述（最多取前 30 条）
    comp_desc = "\n".join(
        f"- {c.get('name', '')} ({c.get('category', '')}): "
        f"损坏等级 {c.get('damage_level', 'N/A')}"
        for c in component_checks[:30]
    )

    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋安全鉴定工程师。请根据以下房屋信息、构件检查记录和损坏情况,"
        '生成"房屋损坏原因分析"的专业描述。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式鉴定报告的最终文本\n"
        "2. 分析内容应包括:材料老化因素、施工质量问题、使用荷载变化、"
        "环境因素影响、地基基础问题、其他可能原因等\n"
        "3. 根据实际损坏情况,分析主要原因和次要原因\n"
        "4. 语言专业、客观、有理有据,符合鉴定报告规范\n"
        "5. 篇幅适中,约150-300字\n"
        "6. 必须使用中文输出\n\n"
        f"房屋信息: {building_profile}\n"
        f"构件检查:\n{comp_desc}\n"
        "请生成最终的房屋损坏原因分析:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_conclusion(
    building_profile: dict = None,
    component_checks: list[dict] = None,
) -> str:
    """生成鉴定报告中"鉴定结论"部分的专业描述。

    对应鉴定报告页面的"鉴定结论"字段。
    根据房屋概况信息和构件检查记录，依据《危险房屋鉴定标准》JGJ 125-2016，
    对地基基础、上部承重结构、围护结构分别进行安全性评定，并给出整体安全性等级。

    Args:
        building_profile: 房屋概况信息字典（包含基本信息、结构信息等）。
        component_checks: 构件检查记录列表，每个记录包含构件名称、分类、AI评定结果等。

    Returns:
        生成的鉴定结论文本（中文），约 100-200 字。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}
    component_checks = component_checks or []

    # 系统提示：设定模型角色为专业的房屋安全鉴定工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋安全鉴定工程师。你必须始终使用中文输出。"
    )

    # 将构件检查列表格式化为可读的文本描述（最多取前 30 条）
    comp_desc = "\n".join(
        f"- {c.get('name', '')} ({c.get('category', '')}): "
        f"评定: {c.get('ai_evaluation_result', 'N/A')}"
        for c in component_checks[:30]
    )

    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋安全鉴定工程师。请根据以下房屋信息、构件检查记录和检测成果,"
        '生成"鉴定结论"的专业描述。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式鉴定报告的最终文本\n"
        "2. 结论应包含:依据的鉴定标准(《危险房屋鉴定标准》JGJ 125-2016)、"
        "各组成部分(地基基础、上部承重结构、围护结构)的评定结果、整体安全性评定结论\n"
        "3. 参考格式:根据《危险房屋鉴定标准》JGJ 125-2016,经现场查勘检测:\n"
        "   1、地基基础安全性评定为Au级;\n   2、上部承重结构安全性评定为Bu级;\n"
        "   3、围护结构安全性评定为Bu级。\n"
        "   综合评定该房屋安全性等级为B级,个别构件危险但不影响主体结构安全。\n"
        "4. 语言专业、规范、结论明确\n5. 篇幅适中,约100-200字\n6. 必须使用中文输出\n\n"
        f"房屋信息: {building_profile}\n"
        f"构件检查:\n{comp_desc}\n"
        "请生成最终的鉴定结论:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_handling_suggestion(
    building_profile: dict = None,
    component_checks: list[dict] = None,
) -> str:
    """生成鉴定报告中"处理意见"部分的专业建议。

    对应鉴定报告页面的"处理意见"字段。
    根据房屋安全性等级（A/B/C/D）给出相应的处理措施建议，
    包括观察使用、处理使用、停止使用或整体拆除等，以及具体的维修加固建议。

    Args:
        building_profile: 房屋概况信息字典（包含基本信息、结构信息等）。
        component_checks: 构件检查记录列表，每个记录包含构件名称、损坏等级等。

    Returns:
        生成的处理意见文本（中文），约 80-150 字。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}
    component_checks = component_checks or []

    # 系统提示：设定模型角色为专业的房屋安全鉴定工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋安全鉴定工程师。你必须始终使用中文输出。"
    )

    # 将构件检查列表格式化为可读的文本描述（最多取前 30 条）
    comp_desc = "\n".join(
        f"- {c.get('name', '')}: 损坏等级 {c.get('damage_level', 'N/A')}"
        for c in component_checks[:30]
    )

    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋安全鉴定工程师。请根据以下房屋信息、构件检查记录和鉴定结论,"
        '生成"处理意见"的专业建议。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式鉴定报告的最终文本\n"
        "2. 处理意见应包括:根据安全性等级给出相应的处理措施(观察使用、处理使用、"
        "停止使用或整体拆除等建议)、具体的维修加固建议(如适用)、后续监测要求(如适用)\n"
        '3. 参考格式:A级则为"该房屋结构安全,可正常使用,建议定期进行检查维护";'
        'B级则为"该房屋个别构件存在危险点,建议对危险构件进行维修加固处理后可继续使用";'
        'C级则为"该房屋局部构成危险,建议停止使用危险区域,并进行整体加固处理";'
        'D级则为"该房屋整体危险,建议立即停止使用,并采取拆除或整体加固措施"\n'
        "4. 语言专业、建议明确、可操作性强\n5. 篇幅适中,约80-150字\n6. 必须使用中文输出\n\n"
        f"房屋信息: {building_profile}\n"
        f"构件检查:\n{comp_desc}\n"
        "请生成最终的处理意见:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_safety_level(
    building_profile: dict = None,
    component_checks: list[dict] = None,
) -> str:
    """判定房屋结构安全等级（A/B/C/D）。

    对应鉴定报告页面的"安全等级判定"字段。
    根据房屋概况信息和构件检查记录，依据《危险房屋鉴定标准》JGJ 125-2016，
    综合判定房屋的整体安全等级（A级、B级、C级或D级）。

    判定标准：
    - A级：结构安全，无危险点，能满足安全使用要求
    - B级：结构基本安全，个别构件有危险点，但不影响主体结构安全
    - C级：局部危险，部分承重结构承载力不能满足正常使用要求
    - D级：整体危险，承重结构承载力已不能满足正常使用要求

    Args:
        building_profile: 房屋概况信息字典（包含基本信息、结构信息等）。
        component_checks: 构件检查记录列表，每个记录包含构件名称、分类、损坏等级、AI评定结果等。

    Returns:
        安全等级字母（A/B/C/D）加上简要理由（50字以内）。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}
    component_checks = component_checks or []

    # 系统提示：设定模型角色为专业的房屋安全鉴定工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋安全鉴定工程师。你必须始终使用中文输出。"
    )

    # 将构件检查列表格式化为可读的文本描述（最多取前 30 条）
    comp_desc = "\n".join(
        f"- {c.get('name', '')} ({c.get('category', '')}): "
        f"损坏等级 {c.get('damage_level', 'N/A')}, "
        f"评定: {c.get('ai_evaluation_result', 'N/A')}"
        for c in component_checks[:30]
    )

    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋安全鉴定工程师。请根据以下房屋信息、构件检查记录和检测成果,"
        '判定"房屋结构安全等级"。\n\n'
        "输出要求:\n"
        "1. 只能输出单个字母:A、B、C 或 D,然后简要说明理由(50字以内)\n"
        "2. 判定标准依据《危险房屋鉴定标准》JGJ 125-2016:\n"
        "   A级:结构安全,无危险点,能满足安全使用要求\n"
        "   B级:结构基本安全,个别构件有危险点,但不影响主体结构安全\n"
        "   C级:局部危险,部分承重结构承载力不能满足正常使用要求\n"
        "   D级:整体危险,承重结构承载力已不能满足正常使用要求\n"
        "3. 综合考虑地基基础、上部承重结构、围护结构状况和损坏构件的数量及严重程度\n"
        "4. 必须使用中文输出\n\n"
        f"房屋信息: {building_profile}\n"
        f"构件检查:\n{comp_desc}\n"
        "请直接输出房屋结构安全等级:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用极低温度（0.1）保证判定结果稳定、一致
    return await generate_chat_completion(messages, temperature=0.1, max_tokens=1024)


async def generate_main_test_content(building_profile: dict = None) -> str:
    """生成检测报告中"主要检测内容"部分的专业描述。

    对应检测报告页面的"主要检测内容"字段。
    根据房屋概况信息（结构类型、层数等），生成符合规范的检测内容描述，
    包括结构现状检查、房屋整体倾斜观测、地基基础检查、上部承重构件检查等。

    Args:
        building_profile: 房屋概况信息字典（包含结构类型、层数、基本信息等）。

    Returns:
        生成的主要检测内容文本（中文），格式为编号列表。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}

    # 系统提示：设定模型角色为专业的房屋结构检测工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋结构检测工程师。你必须始终使用中文输出。"
    )
    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋结构检测工程师。请根据以下房屋概况信息,"
        '生成"主要检测内容"的完整专业描述。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式检测报告的最终文本\n"
        "2. 格式:1、XXXX;2、XXXX;3、XXXX\n"
        "3. 内容应包含以下方面(根据房屋实际情况选择适用项):\n"
        "   结构现状检查、房屋整体倾斜观测、地基基础检查、"
        "上部承重构件检查、围护结构检查、楼地面检查、屋面检查、门窗及设备检查、内外抹灰检查\n"
        "4. 根据房屋结构类型和层数确定具体检测项目\n"
        "5. 语言专业、简洁\n6. 必须使用中文输出\n\n"
        f"房屋概况信息:\n{building_profile}\n\n"
        "请直接生成最终的主要检测内容文本:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_test_standards(main_test_content: str = "") -> str:
    """生成检测报告中"检测依据标准"部分的专业描述。

    对应检测报告页面的"检测依据标准"字段。
    根据主要检测内容，智能选择适用的国家/行业标准，生成符合规范的检测依据描述。

    常用标准包括：
    - 《危险房屋鉴定标准》JGJ 125-2016（结构安全性鉴定必含）
    - 《建筑结构检测技术标准》GB/T 50344-2019（结构检测必含）
    - 《建筑变形测量规范》JGJ 8-2016（含倾斜观测时必含）
    - 《房屋完损等级评定标准》（建设部城住字[84]第678号）（完损评定必含）

    Args:
        main_test_content: 主要检测内容文本，用于智能选择适用标准。

    Returns:
        生成的检测依据标准文本（中文），格式为编号列表。
    """
    # 系统提示：设定模型角色为专业的房屋结构检测工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋结构检测工程师。你必须始终使用中文输出。"
    )
    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        '你是一位专业的房屋结构检测工程师。请根据以下"主要检测内容",'
        '生成"检测依据标准"的完整专业描述。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式检测报告的最终文本\n"
        "2. 格式:1、《规范名称》规范编号;2、《规范名称》规范编号\n"
        "3. 必须包含以下规范中与检测内容相关的标准:\n"
        "   《危险房屋鉴定标准》JGJ 125-2016(结构安全性鉴定必含)\n"
        "   《建筑结构检测技术标准》GB/T 50344-2019(结构检测必含)\n"
        "   《建筑变形测量规范》JGJ 8-2016(含倾斜观测时必含)\n"
        "   《房屋完损等级评定标准》(建设部城住字[84]第678号)(完损评定必含)\n"
        "4. 根据检测内容智能选择适用的规范\n5. 语言规范、准确\n6. 必须使用中文输出\n\n"
        f"主要检测内容:\n{main_test_content or '一般建筑结构评估'}\n\n"
        "请直接生成最终的检测依据标准文本:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=2048)


async def generate_test_results(
    building_profile: dict = None,
    main_test_content: str = "",
    test_standards: str = "",
    component_checks: list[dict] = None,
) -> str:
    """生成检测报告中"主要检测成果"部分的专业描述。

    对应检测报告页面的"主要检测成果"字段。
    根据房屋概况、检测内容、检测依据和构件检查记录，生成符合规范的检测成果描述，
    包括房屋结构构件外观质量检查结果和房屋倾斜观测结果。

    Args:
        building_profile: 房屋概况信息字典（包含结构类型、层数、基本信息等）。
        main_test_content: 主要检测内容文本。
        test_standards: 检测依据标准文本。
        component_checks: 构件检查记录列表，每个记录包含构件名称、分类、损坏等级等。

    Returns:
        生成的主要检测成果文本（中文），包含外观质量检查和倾斜观测结果。
    """
    # 处理默认值，避免 None 导致错误
    building_profile = building_profile or {}
    component_checks = component_checks or []

    # 系统提示：设定模型角色为专业的房屋结构检测工程师，强制中文输出
    system_prompt = (
        "你是一位专业的房屋结构检测工程师。你必须始终使用中文输出。"
    )
    # 用户提示：详细描述任务要求、输出规则和输入数据
    user_prompt = (
        "你是一位专业的房屋结构检测工程师。请根据以下房屋概况、检测内容、"
        '检测依据和构件检查记录,生成"主要检测成果"的完整专业描述。\n\n'
        "输出要求:\n"
        "1. 直接输出可用于正式检测报告的最终文本\n"
        "2. 严格按照以下格式:\n"
        "现场检测结果如下:\n"
        "1、房屋结构构件外观质量检查结果:\n"
        "(1)地基;(2)基础;(3)上部承重构件;(4)围护结构承重构件;\n"
        "(5)内抹灰;(6)楼地面;(7)屋面;(8)门窗及设备;(9)外抹灰\n"
        "2、房屋倾斜观测:\n"
        '3. 根据构件检查记录客观描述各部位现状,无异常则用"基本完好"等表述\n'
        "4. 语言专业、客观,符合检测报告规范\n5. 必须使用中文输出\n\n"
        f"房屋概况信息:{building_profile}\n"
        f"主要检测内容:{main_test_content}\n"
        f"检测依据标准:{test_standards}\n"
        f"构件检查记录:{component_checks}\n\n"
        "请直接生成最终的主要检测成果文本:"
    )
    # 构建消息列表（系统提示 + 用户提示）
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    # 调用 Chat Completion API，使用低温度（0.3）保证输出稳定一致
    return await generate_chat_completion(messages, temperature=0.3, max_tokens=1024)
