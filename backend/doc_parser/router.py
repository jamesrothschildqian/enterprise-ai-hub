"""
文档智能解析模块 (AI文档工厂) - API路由
支持：上传解析、Mock演示、模板列表、批量解析
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Query
from doc_parser.service import list_templates, mock_parse, parse_upload, batch_parse_demo
from config.settings import settings

router = APIRouter(tags=["文档智能解析 / DocParser"])


@router.get(
    "/templates",
    summary="获取文档模板列表",
    description="根据当前选中行业，返回对应的文档模板列表（包含文档类型、字段定义等）",
)
def api_list_templates(
    industry_id: Optional[str] = Query(None, description="行业ID，不传则使用当前选中行业"),
):
    ind = industry_id or settings.current_industry
    return list_templates(ind)


@router.get(
    "/demo/{template_id}",
    summary="Mock演示解析",
    description="无需上传文件，直接使用预置的Mock数据演示文档解析效果，返回提取的结构化字段",
)
def api_mock_parse(
    template_id: str,
    industry_id: Optional[str] = Query(None, description="行业ID，不传则使用当前选中行业"),
):
    ind = industry_id or settings.current_industry
    return mock_parse(ind, template_id)


@router.post(
    "/parse",
    summary="上传解析文档",
    description="上传PDF/图片/文本文件，自动识别文档类型并提取结构化字段<br>"
                "支持格式：PDF、PNG/JPG、TXT<br>"
                "Mock模式下会调用模拟OCR+NLP流程，无需真实API密钥",
)
async def api_parse_upload(
    file: UploadFile = File(..., description="待解析的文档文件"),
    doc_type: Optional[str] = Form(None, description="手动指定文档类型，不传则自动识别"),
    industry_id: Optional[str] = Form(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return await parse_upload(ind, file, doc_type)


@router.get(
    "/batch-demo",
    summary="批量演示解析",
    description="批量解析当前行业所有Mock文档，一次性返回所有文档的提取结果",
)
def api_batch_demo(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return {"results": batch_parse_demo(ind), "total": 0}
