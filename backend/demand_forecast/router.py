"""
需求预测分析模块 - API路由
提供：历史数据查询、预测运行、AI洞察分析
"""
from typing import Optional
from typing import Optional
from fastapi import APIRouter, Query, Body
from demand_forecast.service import get_metrics, get_history, run_prediction, get_llm_insight
from config.settings import settings

router = APIRouter(tags=["需求预测分析 / DemandForecast"])


@router.get(
    "/metrics",
    summary="获取预测指标列表",
    description="返回当前行业的业务指标定义（如：出口订单量、产量、贷款申请量等）",
)
def api_metrics(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"industry_id": ind, "metrics": get_metrics(ind)}


@router.get(
    "/history",
    summary="获取历史数据",
    description="获取当前行业的历史业务数据（用于前端展示原始趋势）",
)
def api_history(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"industry_id": ind, "history": get_history(ind)}


@router.post(
    "/predict",
    summary="运行需求预测",
    description="基于历史数据，使用加权移动平均+趋势外推算法预测未来N天(默认30天)的业务指标<br>"
                "返回ECharts兼容的图表数据格式，可直接用于前端渲染",
)
def api_predict(
    periods: int = Body(30, embed=True, description="预测天数(1-90)"),
    industry_id: Optional[str] = Body(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return run_prediction(ind, periods)


@router.get(
    "/data",
    summary="获取完整预测数据",
    description="一键获取：历史数据 + 未来30天预测数据 + ECharts图表配置 + 置信度",
)
def api_data(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return run_prediction(ind, 30)


@router.get(
    "/insight",
    summary="AI预测洞察",
    description="调用大模型分析预测结果，生成文字版经营建议和洞察分析",
)
def api_insight(
    metric_key: Optional[str] = Query(None, description="指定指标key，为空则分析全部"),
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"insight": get_llm_insight(ind, metric_key or "")}
