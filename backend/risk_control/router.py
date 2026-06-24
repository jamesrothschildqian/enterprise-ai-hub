"""
风险控制中心模块 - API路由
提供：风险指标监控、交易分析、异常检测、风险评估
"""
from typing import Optional, List
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from risk_control.service import (
    get_risk_indicators, assess_risk, analyze_transactions, detect_anomalies, get_risk_labels,
)
from config.settings import settings

router = APIRouter(tags=["风险控制中心 / RiskControl"])


class TransactionAnalysisRequest(BaseModel):
    transactions: Optional[List[dict]] = Body(None, description="交易流水数据（不传则使用Mock数据）")
    industry_id: Optional[str] = Body(None, description="行业ID")


class AnomalyDetectionRequest(BaseModel):
    data: Optional[List[dict]] = Body(None, description="待检测数据（不传则使用Mock数据）")
    industry_id: Optional[str] = Body(None, description="行业ID")


@router.get(
    "/labels",
    summary="获取风险标签",
    description="返回当前行业的所有风险标签定义（含严重等级和描述）",
)
def api_labels(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"industry_id": ind, "risk_labels": get_risk_labels(ind)}


@router.get(
    "/indicators",
    summary="获取风险指标",
    description="返回当前行业的风险指标看板数据：综合评分、各维度指标详情、趋势方向",
)
def api_indicators(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return get_risk_indicators(ind)


@router.post(
    "/assess",
    summary="整体风险评估",
    description="对当前行业进行整体风险评估，返回综合评分、风险等级和处置建议",
)
def api_assess(
    industry_id: Optional[str] = Body(None, embed=True, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return assess_risk(ind)


@router.post(
    "/analyze-transactions",
    summary="交易风险分析",
    description="导入交易流水数据，通过规则引擎+大模型双重分析识别风险<br>"
                "不传数据时使用当前行业的Mock数据演示",
)
def api_analyze(req: TransactionAnalysisRequest):
    ind = req.industry_id or settings.current_industry
    return analyze_transactions(ind, req.transactions)


@router.post(
    "/detect-anomalies",
    summary="异常检测",
    description="规则+大模型双重异常检测，支持自定义数据或使用Mock数据演示<br>"
                "返回异常清单（含类型、严重等级、描述）",
)
def api_detect(req: AnomalyDetectionRequest):
    ind = req.industry_id or settings.current_industry
    return detect_anomalies(ind, req.data)
