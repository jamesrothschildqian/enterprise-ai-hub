"""
文档智能解析模块 - 业务逻辑层 (AI文档工厂)
提供文档解析、字段提取、Prompt模板管理等功能
不同行业自动切换不同的字段规则和解析Prompt
"""
import json
import os
import tempfile
from typing import Optional
from fastapi import UploadFile

from config.config_engine import get_doc_parser_config, get_doc_parser_mock
from config.settings import settings
from utils.ai_llm import AILLM
from utils.ocr_helper import extract_text_from_upload, get_demo_content


def list_templates(industry_id: str) -> dict:
    """
    获取指定行业的文档模板列表
    返回该行业所有可解析的文档类型定义
    """
    cfg = get_doc_parser_config(industry_id)
    doc_types = cfg.get("document_types", [])
    field_rules = cfg.get("field_rules", {})
    templates = []
    for dt in doc_types:
        templates.append({
            "id": dt["id"],
            "name": dt["name"],
            "description": dt["description"],
            "fields": field_rules.get(dt["id"], []),
        })
    return {
        "industry_id": industry_id,
        "templates": templates,
    }


def get_parse_prompt(industry_id: str, doc_type: str, doc_text: str) -> str:
    """
    获取指定行业+文档类型的解析Prompt
    从 industry_config.json 读取对应的 Prompt 模板
    """
    cfg = get_doc_parser_config(industry_id)
    prompts = cfg.get("prompt_templates", {})
    field_rules = cfg.get("field_rules", {})
    fields = field_rules.get(doc_type, [])
    fields_str = "、".join(fields)

    # 优先使用文档类型特定的Prompt，否则使用default
    prompt_tpl = prompts.get(doc_type) or prompts.get("default", "")
    return prompt_tpl.replace("{doc_type}", doc_type) \
                     .replace("{document_text}", doc_text) \
                     .replace("{fields}", fields_str)


def parse_with_llm(industry_id: str, doc_type: str, doc_text: str) -> dict:
    """
    使用大模型解析文档内容
    支持 Mock / DeepSeek / OpenAI 三种模式
    """
    prompt = get_parse_prompt(industry_id, doc_type, doc_text)
    llm = AILLM()
    messages = [
        {"role": "system", "content": "你是一个文档解析专家。请严格按照要求的字段提取信息，返回合法JSON。"},
        {"role": "user", "content": prompt},
    ]
    result = llm.chat_with_json(messages)
    return result


def mock_parse(industry_id: str, template_id: str) -> dict:
    """
    Mock解析演示：从mock数据或demo_resource中获取预置文档，模拟AI解析效果
    无需API密钥即可展示文档解析能力
    """
    import random
    docs = get_doc_parser_mock(industry_id)
    cfg = get_doc_parser_config(industry_id)
    field_rules = cfg.get("field_rules", {})

    # 查找匹配的文档
    target = next((d for d in docs if d["type"] == template_id), None)
    if not target and docs:
        target = docs[0]

    # 尝试从 demo_resource 读取内容
    demo_content = get_demo_content(industry_id, template_id)
    doc_title = target.get("title", "") if target else f"{template_id} 模拟文档"
    doc_type = target.get("type", template_id) if target else template_id

    if not target and not demo_content:
        # 动态生成模拟字段
        fields = field_rules.get(template_id, [])
        extracted = {f: f"mock_{random.randint(100,999)}" for f in fields[:6]}
        return {
            "template_id": template_id,
            "document_title": f"{template_id} (动态生成)",
            "document_type": template_id,
            "fields_count": len(extracted),
            "extracted_fields": extracted,
            "parse_method": "dynamic_mock_parser",
        }

    fields = field_rules.get(doc_type, list(target.get("fields", {}).keys())) if target else []
    extracted = target.get("fields", {}) if target else {}
    missing = [f for f in fields if f not in extracted]

    content_preview = target.get("content", "")[:300] if target else (demo_content or "")[:300]

    return {
        "template_id": template_id,
        "document_title": doc_title,
        "document_type": doc_type,
        "fields_count": len(extracted),
        "extracted_fields": extracted,
        "missing_fields": missing,
        "raw_preview": content_preview,
        "parse_method": "mock_ai_parser",
    }


async def parse_upload(industry_id: str, file: UploadFile, doc_type: Optional[str] = None) -> dict:
    """
    解析用户上传的文档文件
    支持 PDF / 图片 / 文本文件
    真实环境下对接PaddleOCR进行文字识别，然后调用大模型提取字段
    """
    # 保存上传文件到临时目录
    suffix = os.path.splitext(file.filename or "upload.txt")[1] or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        file_size = len(content)
        file_type = suffix.lower()

        # 轻量化 OCR 流程：优先从 demo_resource 读取预置内容，
        # 失败时尝试大模型 OCR，无需本地 OCR 模型
        text_content = extract_text_from_upload(content, file.filename or "", industry_id)

        # 自动推断文档类型
        inferred_type = doc_type or _infer_doc_type(industry_id, text_content)
        cfg = get_doc_parser_config(industry_id)
        field_rules = cfg.get("field_rules", {})
        expected_fields = field_rules.get(inferred_type, [])

        # LLM解析
        llm_result = parse_with_llm(industry_id, inferred_type, text_content[:2000])

        return {
            "filename": file.filename,
            "file_size": file_size,
            "file_type": file_type,
            "industry_id": industry_id,
            "document_type": inferred_type,
            "parse_status": "success",
            "extracted_fields": llm_result if isinstance(llm_result, dict) else {"raw": llm_result},
            "expected_fields": expected_fields,
            "ocr_engine": "llm_ocr" if settings.ai_provider != "mock" else "demo_resource_reader",
            "nlp_engine": f"{settings.ai_provider}_parser",
        }
    finally:
        os.unlink(tmp_path)


def _infer_doc_type(industry_id: str, text: str) -> str:
    """
    根据文档内容关键词自动推断文档类型
    """
    cfg = get_doc_parser_config(industry_id)
    doc_types = cfg.get("document_types", [])
    for dt in doc_types:
        keywords = {
            "customs_declaration": ["报关单", "商品编码", "经营单位"],
            "letter_of_credit": ["信用证", "开证行", "受益人"],
            "commercial_invoice": ["发票", "卖方", "买方", "单价"],
            "bill_of_lading": ["提单", "船名", "装货港"],
            "production_order": ["工单", "产线", "计划数量"],
            "qc_report": ["质检", "检验项目", "判定结果"],
            "credit_contract": ["贷款合同", "借款人", "年利率"],
            "financial_report": ["资产负债表", "利润表", "营业收入"],
            "labor_contract": ["劳动合同", "员工姓名", "基本工资"],
            "resume": ["简历", "毕业院校", "工作年限"],
            "engineering_change": ["签证单", "变更内容", "施工单位"],
            "sales_contract": ["买卖合同", "成交总价", "房屋坐落"],
        }
        for kw in keywords.get(dt["id"], []):
            if kw in text:
                return dt["id"]
    return doc_types[0]["id"] if doc_types else "default"


def batch_parse_demo(industry_id: str) -> list:
    """批量演示解析该行业所有mock文档"""
    docs = get_doc_parser_mock(industry_id)
    results = []
    for doc in docs:
        results.append({
            "id": doc["id"],
            "type": doc["type"],
            "title": doc.get("title", ""),
            "fields": doc.get("fields", {}),
        })
    return results
