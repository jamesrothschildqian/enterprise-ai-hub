"""
演示用例 API 路由
提供：演示用例列表查询、单个用例执行、模块用例执行
"""

from typing import Optional
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from config.settings import settings
from services.demo_cases import get_demo_cases, execute_demo_case

router = APIRouter(tags=["演示用例 / DemoCases"])


class ExecuteRequest(BaseModel):
    case_id: str = Body(..., description="演示用例ID")
    industry_id: Optional[str] = Body(None, description="行业ID")


@router.get(
    "/cases",
    summary="获取演示用例列表",
    description="返回所有可用的演示用例（每模块3个，共15个），可按模块筛选",
)
def api_list_cases(
    module: Optional[str] = Query(None, description="模块名: doc_parser / demand_forecast / ai_agent / risk_control / chatbi"),
):
    return {"cases": get_demo_cases(module), "total": len(get_demo_cases(module))}


@router.post(
    "/execute",
    summary="执行演示用例",
    description="一键执行指定演示用例，直接返回演示结果数据",
)
def api_execute_case(req: ExecuteRequest):
    ind = req.industry_id or settings.current_industry
    return execute_demo_case(req.case_id, ind)
