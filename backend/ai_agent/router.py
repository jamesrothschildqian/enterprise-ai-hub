"""
AI智能助手模块 - API路由
提供：多轮对话、知识库查询、批量文案生成
"""
from typing import Optional, List, Dict
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from ai_agent.service import chat, get_knowledge_base, get_greeting, get_capabilities, batch_generate
from config.settings import settings

router = APIRouter(tags=["AI智能助手 / AIAgent"])


class ChatRequest(BaseModel):
    message: str = Body(..., description="用户消息")
    history: Optional[List[Dict[str, str]]] = Body([], description="对话历史 [{'role':'user/assistant','content':'...'}]")
    industry_id: Optional[str] = Body(None, description="行业ID")


class BatchGenerateRequest(BaseModel):
    generate_type: str = Body(..., description="生成类型: marketing/invitation")
    params: dict = Body({}, description="生成参数")
    count: int = Body(3, description="生成数量(1-10)")
    industry_id: Optional[str] = Body(None, description="行业ID")


@router.get(
    "/greeting",
    summary="获取打招呼语",
    description="返回当前行业的AI助手欢迎语",
)
def api_greeting(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"industry_id": ind, "greeting": get_greeting(ind)}


@router.get(
    "/capabilities",
    summary="获取能力列表",
    description="返回当前行业AI助手擅长的能力范围",
)
def api_capabilities(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"industry_id": ind, "capabilities": get_capabilities(ind)}


@router.get(
    "/knowledge",
    summary="获取知识库",
    description="返回当前行业的知识库问答列表，包含所有预置的问答对",
)
def api_knowledge(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return get_knowledge_base(ind)


@router.post(
    "/chat",
    summary="AI对话",
    description="多轮对话接口，根据当前行业自动加载对应的System Prompt和知识库<br>"
                "支持Mock/DeepSeek/OpenAI三种模式<br>"
                "对话历史最多保留最近10轮",
)
def api_chat(req: ChatRequest):
    ind = req.industry_id or settings.current_industry
    return chat(ind, req.message, req.history)


@router.post(
    "/batch-generate",
    summary="批量生成文案",
    description="批量生成营销/邀约文案，支持指定行业、生成类型和参数<br>"
                "marketing: 营销推广文案<br>"
                "invitation: 邀约函/邀请函",
)
def api_batch_generate(req: BatchGenerateRequest):
    ind = req.industry_id or settings.current_industry
    count = max(1, min(req.count, 10))
    return batch_generate(ind, req.generate_type, req.params, count)
