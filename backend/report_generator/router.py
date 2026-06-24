"""
行业落地Case报告生成 - API路由
提供：报告生成、行业摘要列表
"""

from typing import Optional
from fastapi import APIRouter, Query
from config.settings import settings
from report_generator.service import generate_report, get_all_reports_summary

router = APIRouter(tags=["行业落地报告 / Report"])


@router.get(
    "/report",
    summary="生成行业落地Case报告",
    description="AI自动生成当前行业的落地效果报告，含痛点描述、AI解决方案、ROI数据。PDF预览数据。",
)
def api_generate_report(
    industry_id: Optional[str] = Query(None, description="行业ID，不传则使用当前选中行业"),
):
    ind = industry_id or settings.current_industry
    return generate_report(ind)


@router.get(
    "/reports-summary",
    summary="获取所有行业报告摘要",
    description="返回所有6个行业的报告摘要列表（含ROI百分比、年节省、投资回报等）",
)
def api_reports_summary():
    return {"summaries": get_all_reports_summary()}
