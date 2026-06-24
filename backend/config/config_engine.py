"""
全局配置引擎
职责：
1. 加载 industry_config.json (字段规则、Prompt模板、风险标签等)
2. 加载 mock_data/{industry}.json (各行业演示数据)
3. 提供统一获取接口，所有模块通过此引擎访问配置和数据
"""
import json
import os
import threading
from typing import Any, Dict, Optional

# 文件路径常量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "industry_config.json")
MOCK_DATA_DIR = os.path.join(BASE_DIR, "mock_data")

# 全局缓存
_config_cache: Optional[Dict[str, Any]] = None
_mock_cache: Dict[str, Optional[Dict[str, Any]]] = {}

# 请求级别语言设置（通过 middleware 设置）
_request_local = threading.local()


def set_lang(lang: str) -> None:
    """设置当前请求的语言"""
    _request_local.lang = lang


def get_lang() -> str:
    """获取当前请求的语言，默认 'en'"""
    return getattr(_request_local, 'lang', 'en')


def _load_config() -> Dict[str, Any]:
    """加载 industry_config.json (带缓存)"""
    global _config_cache
    if _config_cache is None:
        with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
            _config_cache = json.load(f)
    return _config_cache


def _load_mock(industry_id: str) -> Dict[str, Any]:
    """加载指定行业的 mock_data JSON (带缓存)，根据当前语言自动选择文件"""
    global _mock_cache
    lang = get_lang()
    cache_key = f"{industry_id}_{lang}"
    if cache_key not in _mock_cache:
        if lang == "zh":
            filename = f"{industry_id}.json"
        else:
            filename = f"{industry_id}_{lang}.json"
        path = os.path.join(MOCK_DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8-sig") as f:
                _mock_cache[cache_key] = json.load(f)
        else:
            _mock_cache[cache_key] = {}
    return _mock_cache[cache_key] or {}


def get_industry_config(industry_id: str) -> Dict[str, Any]:
    """获取指定行业的完整配置，根据当前语言自动返回对应语言内容"""
    config = _load_config()
    cfg = config.get(industry_id, {})
    lang = get_lang()
    if lang != "zh":
        cfg = _translate_config(cfg, lang)
    return cfg


def _translate_config(cfg: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """Recursively replace *_{lang} fields into base fields for given language output"""
    import copy
    result = copy.deepcopy(cfg)
    _apply_lang(result, lang)
    return result


def _apply_lang(d: Any, suffix: str) -> None:
    """Walk dict/list and promote key_{suffix} -> key"""
    if isinstance(d, dict):
        suffix_key = f"_{suffix}"
        lang_keys = [k for k in d if k.endswith(suffix_key)]
        for lk in lang_keys:
            base = lk[:-len(suffix_key)]
            d[base] = d[lk]
            del d[lk]
        for v in d.values():
            _apply_lang(v, suffix)
    elif isinstance(d, list):
        for item in d:
            _apply_lang(item, suffix)


def get_industry_basic(industry_id: str) -> Dict[str, str]:
    """获取行业基本信息 (name, name_en, description)"""
    return get_industry_config(industry_id).get("basic", {})


# ─── doc_parser 模块接口 ─────────────────────────────────


def get_doc_parser_config(industry_id: str) -> Dict[str, Any]:
    """获取文档解析模块的配置 (字段规则 + Prompt模板)"""
    return get_industry_config(industry_id).get("doc_parser", {})


def get_doc_parser_mock(industry_id: str) -> list:
    """获取文档解析的 mock 文档数据"""
    mock = _load_mock(industry_id)
    return mock.get("doc_parser", {}).get("documents", [])


# ─── demand_forecast 模块接口 ───────────────────────────


def get_forecast_config(industry_id: str) -> Dict[str, Any]:
    """获取需求预测模块的配置 (指标定义)"""
    return get_industry_config(industry_id).get("demand_forecast", {})


def get_forecast_mock(industry_id: str) -> list:
    """获取需求预测的 mock 历史数据"""
    mock = _load_mock(industry_id)
    return mock.get("demand_forecast", {}).get("history", [])


# ─── ai_agent 模块接口 ──────────────────────────────────


def get_ai_agent_config(industry_id: str) -> Dict[str, Any]:
    """获取AI智能助手模块的配置 (System Prompt + 能力列表 + 批量生成模板)"""
    return get_industry_config(industry_id).get("ai_agent", {})


def get_ai_agent_mock(industry_id: str) -> list:
    """获取AI智能助手的 mock 知识库"""
    mock = _load_mock(industry_id)
    return mock.get("ai_agent", {}).get("knowledge_base", [])


# ─── risk_control 模块接口 ──────────────────────────────


def get_risk_config(industry_id: str) -> Dict[str, Any]:
    """获取风控模块的配置 (风险标签 + 规则定义)"""
    return get_industry_config(industry_id).get("risk_control", {})


def get_risk_mock(industry_id: str) -> Dict[str, Any]:
    """获取风控模块的 mock 数据 (交易流水 + 指标)"""
    mock = _load_mock(industry_id)
    return mock.get("risk_control", {})


# ─── chatbi 模块接口 ────────────────────────────────────


def get_chatbi_config(industry_id: str) -> Dict[str, Any]:
    """获取自然语言BI模块的配置 (表结构 + 查询Prompt)"""
    return get_industry_config(industry_id).get("chatbi", {})


def get_chatbi_mock(industry_id: str) -> dict:
    """获取BI模块的 mock 业务数据表"""
    mock = _load_mock(industry_id)
    return mock.get("chatbi", {}).get("tables", {})


# ─── 通用工具 ──────────────────────────────────────────


def get_all_industries() -> list:
    """获取所有行业列表 (供前端下拉框使用)"""
    config = _load_config()
    result = []
    for ind_id, ind_cfg in config.items():
        basic = ind_cfg.get("basic", {})
        item = {
            "id": ind_id,
            "name": basic.get("name", ind_id),
            "name_en": basic.get("name_en", ""),
            "name_vi": basic.get("name_vi", ""),
            "name_ms": basic.get("name_ms", ""),
            "description": basic.get("description", ""),
        }
        result.append(item)
    return result


def reload():
    """清空缓存，强制重新加载 (调试用)"""
    global _config_cache, _mock_cache
    _config_cache = None
    _mock_cache = {}
