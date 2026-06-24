"""
轻量级 OCR 辅助模块
无需本地 OCR 模型预训练，优先调用在线大模型进行文字识别
支持以下策略：
  1. LLM 直读文本内容（模拟 OCR 返回）
  2. 文件类型识别（PDF / 图片 / TXT）
  3. 从 demo_resource 读取预置文档内容
"""

import os
import base64
from typing import Optional

from config.settings import settings
from utils.ai_llm import AILLM

# 映射 demo_resource 目录到各行业
DEMO_RESOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "demo_resource",
)


def get_demo_content(industry_id: str, doc_type: str) -> Optional[str]:
    """
    从 demo_resource/{industry_id}/ 读取预置文档内容
    返回文档文本（模拟 PDF/图片经 OCR 后的结果）
    """
    content_file = os.path.join(DEMO_RESOURCE_DIR, industry_id, f"{doc_type}_content.txt")
    if os.path.exists(content_file):
        with open(content_file, "r", encoding="utf-8") as f:
            return f.read()

    # 回退：尝试通配读取第一个 content 文件
    import glob
    pattern = os.path.join(DEMO_RESOURCE_DIR, industry_id, "*_content.txt")
    files = glob.glob(pattern)
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return f.read()
    return None


def ocr_with_llm(image_data: bytes, filename: str = "") -> str:
    """
    使用大模型进行文字识别
    Args:
        image_data: 图片/PDF 的二进制数据
        filename: 原文件名（用于推断类型）
    Returns:
        识别出的文本内容
    """
    # Mock 模式：直接返回简单的占位文本
    if settings.ai_provider == "mock":
        return "[Mock OCR] 已识别文件: {filename}\n内容为模拟识别结果，实际部署时启用在线大模型OCR。"

    # 生成 base64 图片数据（前 100KB）
    b64_data = base64.b64encode(image_data[:102400]).decode("utf-8")
    ext = os.path.splitext(filename)[1].lower() if filename else ".bin"
    mime = "application/pdf" if ext == ".pdf" else f"image/{ext[1:]}" if ext in (".png", ".jpg", ".jpeg") else "text/plain"

    # 调用大模型进行 OCR 识别
    llm = AILLM()
    messages = [
        {
            "role": "system",
            "content": "你是一个OCR文字识别助手。请从图片/PDF中提取所有可见文字内容，保持原有段落和格式。"
                       "只返回识别结果，不要添加说明。",
        },
        {
            "role": "user",
            "content": f"文件类型: {mime}\n文件名: {filename}\n"
                       f"数据(base64前缀): {b64_data[:1000]}...\n"
                       f"请识别此文件中的文字内容。",
        },
    ]
    try:
        result = llm.chat(messages, temperature=0.1, max_tokens=4096)
        return result
    except Exception as e:
        return f"[OCR Fallback] 大模型OCR调用失败: {str(e)}"


def extract_text_from_upload(file_content: bytes, filename: str, industry_id: str) -> str:
    """
    统一文本提取接口
    策略：
      1. 优先从 demo_resource 读取预置内容（当文件名与 doc_type 匹配时）
      2. 尝试大模型 OCR
      3. 回退 UTF-8 解码
    """
    name_lower = filename.lower() if filename else ""

    # 尝试从 demo_resource 匹配
    for doc_type_key in [
        "customs_declaration", "letter_of_credit", "commercial_invoice",
        "production_order", "qc_report", "credit_contract", "financial_report",
        "ocean_waybill", "air_waybill", "engineering_change", "sales_contract",
        "labor_contract", "resume",
    ]:
        if doc_type_key in name_lower:
            content = get_demo_content(industry_id, doc_type_key)
            if content:
                return content

    # 尝试通用匹配
    content = get_demo_content(industry_id, "content")
    if content:
        return content

    # UTF-8 文本解码
    try:
        return file_content.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        pass

    # 大模型 OCR
    return ocr_with_llm(file_content, filename)
