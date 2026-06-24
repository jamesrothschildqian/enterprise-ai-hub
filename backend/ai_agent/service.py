"""
AI智能助手模块 - 业务逻辑层
支持：多轮对话、行业知识库问答、批量文案生成
根据当前行业自动加载对应的System Prompt和知识库
"""
import random
from typing import List, Dict, Optional

from config.config_engine import get_ai_agent_config, get_ai_agent_mock
from utils.ai_llm import AILLM


def get_system_prompt(industry_id: str) -> str:
    """获取当前行业的系统提示词"""
    cfg = get_ai_agent_config(industry_id)
    return cfg.get("system_prompt", "你是一个AI智能助手，请用中文回答。")


def get_greeting(industry_id: str) -> str:
    """获取当前行业的打招呼语"""
    cfg = get_ai_agent_config(industry_id)
    return cfg.get("greeting", "您好！我是AI智能助手。")


def get_capabilities(industry_id: str) -> list:
    """获取当前行业的能力列表"""
    cfg = get_ai_agent_config(industry_id)
    return cfg.get("capabilities", [])


def get_knowledge_base(industry_id: str) -> dict:
    """获取当前行业的知识库（问答对）"""
    kb = get_ai_agent_mock(industry_id)
    cfg = get_ai_agent_config(industry_id)
    return {
        "industry_id": industry_id,
        "knowledge_base": kb,
        "capabilities": cfg.get("capabilities", []),
    }


def chat(industry_id: str, message: str, history: Optional[List[Dict]] = None) -> dict:
    """
    多轮对话接口
    1. 加载行业System Prompt
    2. 组装完整对话历史
    3. 调用AI大模型回复
    4. Mock模式下使用知识库匹配+默认回复
    """
    if history is None:
        history = []
    system_prompt = get_system_prompt(industry_id)
    knowledge = get_ai_agent_mock(industry_id)

    # 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]
    # 添加上下文（最多保留最近10轮）
    for h in history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})

    # 调用AI
    llm = AILLM()
    reply = llm.chat(messages)

    # 尝试知识库匹配
    matched_qa = _match_knowledge(message, knowledge)

    return {
        "reply": reply,
        "industry_id": industry_id,
        "knowledge_matched": matched_qa is not None,
        "matched_question": matched_qa["question"] if matched_qa else None,
    }


def _match_knowledge(query: str, knowledge: list) -> Optional[dict]:
    """关键词匹配知识库"""
    query_lower = query.lower()
    for item in knowledge:
        q = item.get("question", "")
        if any(kw in query for kw in q[:10]) or any(kw in q for kw in query[:10]):
            return item
        # 检查关键词交集
        q_words = set(q.replace("?", "").replace("？", "").split())
        q_words = {w for w in q_words if len(w) > 1}
        query_words = set(query.replace("?", "").replace("？", "").split())
        query_words = {w for w in query_words if len(w) > 1}
        if len(q_words & query_words) >= 2:
            return item
    return None


def batch_generate(industry_id: str, generate_type: str, params: dict, count: int = 3) -> dict:
    """
    批量生成营销/邀约文案
    Args:
        industry_id: 行业ID
        generate_type: "marketing" | "invitation"
        params: 生成参数 (如 {company_name, product, target_market})
        count: 生成数量
    Returns:
        生成的文案列表
    """
    cfg = get_ai_agent_config(industry_id)
    prompts = cfg.get("batch_generation_prompts", {})
    prompt_tpl = prompts.get(generate_type, "")
    if not prompt_tpl:
        return {"error": f"不支持生成类型: {generate_type}"}

    # 替换参数
    prompt = prompt_tpl
    for k, v in params.items():
        placeholder = "{" + k + "}"
        prompt = prompt.replace(placeholder, str(v))

    llm = AILLM()
    results = []
    for i in range(count):
        msg = prompt + f"\n\n请生成第{i+1}版，风格多样化。不要重复前面版本的内容。"
        reply = llm.chat([{"role": "user", "content": msg}])
        results.append({"version": i + 1, "content": reply})

    return {
        "industry_id": industry_id,
        "generate_type": generate_type,
        "count": count,
        "results": results,
    }
