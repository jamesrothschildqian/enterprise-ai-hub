"""
统一演示用例模块
为每个模块提供 3 个一键演示用例
前端【加载样例】按钮可直接调用这些接口，快速出演示结果
"""

import json
from typing import Optional
from config.settings import settings
from config.config_engine import get_doc_parser_config, get_forecast_config, \
    get_ai_agent_config, get_risk_config, get_chatbi_config, get_doc_parser_mock, \
    get_forecast_mock, get_ai_agent_mock, get_risk_mock, get_chatbi_mock

# ─── doc_parser 演示用例 ──────────────────────────────────

DOC_CASES: dict = {
    "case_1": {
        "id": "doc_case_1",
        "title": "解析演示文档（自动识别类型）",
        "description": "从demo_resource读取预置文档内容，调用AI大模型提取结构化字段。无需上传文件。",
        "module": "doc_parser",
        "params": {"template_id": ""},
    },
    "case_2": {
        "id": "doc_case_2",
        "title": "批量解析全部行业文档",
        "description": "一键解析当前行业全部预置文档模板（4种文档类型），对比各文档提取结果。",
        "module": "doc_parser",
        "params": {},
    },
    "case_3": {
        "id": "doc_case_3",
        "title": "文档类型自动推断演示",
        "description": "上传一段合同文本，系统自动推断文档类型并提取关键字段。展示AI文档分类能力。",
        "module": "doc_parser",
        "params": {"sample_text": "合同编号: CT-2024-0889\n买方: Global Trade Solutions GmbH\n商品: 精密轴承套件\n总金额: EUR 142,500.00"},
    },
}

# ─── demand_forecast 演示用例 ─────────────────────────────

FORECAST_CASES: dict = {
    "case_1": {
        "id": "forecast_case_1",
        "title": "7日快速预测",
        "description": "基于近30天历史数据，使用加权移动平均算法预测未来7天业务趋势。快速出图。",
        "module": "demand_forecast",
        "params": {"periods": 7},
    },
    "case_2": {
        "id": "forecast_case_2",
        "title": "30日完整预测 + AI洞察",
        "description": "运行完整30天预测，并调用大模型生成文字版经营分析和建议。适合POC深度展示。",
        "module": "demand_forecast",
        "params": {"periods": 30, "insight": True},
    },
    "case_3": {
        "id": "forecast_case_3",
        "title": "全部指标对比分析",
        "description": "同时展示当前行业所有业务指标（如出口订单量、出口金额、新增客户数）的预测趋势，对比分析。",
        "module": "demand_forecast",
        "params": {"periods": 30, "all_metrics": True},
    },
}

# ─── ai_agent 演示用例 ───────────────────────────────────

AGENT_CASES: dict = {
    "case_1": {
        "id": "agent_case_1",
        "title": "AI智能对话（多轮交互）",
        "description": "向AI助手发送行业问题，展示多轮对话能力。支持Mock/DeepSeek/OpenAI三种模式。",
        "module": "ai_agent",
        "params": {"message": "请介绍一下当前行业的最新业务趋势和发展建议。"},
    },
    "case_2": {
        "id": "agent_case_2",
        "title": "行业知识库问答",
        "description": "从行业知识库中匹配最佳问答对，演示AI助手的行业专业知识应答能力。",
        "module": "ai_agent",
        "params": {"message": ""},
    },
    "case_3": {
        "id": "agent_case_3",
        "title": "批量文案生成（营销+邀约）",
        "description": "一键生成3版营销文案+3版邀约函，展示批量生成和风格多样化的能力。",
        "module": "ai_agent",
        "params": {"generate_type": "marketing", "company": "示例科技有限公司"},
    },
}

# ─── risk_control 演示用例 ───────────────────────────────

RISK_CASES: dict = {
    "case_1": {
        "id": "risk_case_1",
        "title": "导入交易数据并分析风险",
        "description": "加载当前行业Mock交易流水数据，通过规则引擎+AI双重检测，标记风险交易。",
        "module": "risk_control",
        "params": {},
    },
    "case_2": {
        "id": "risk_case_2",
        "title": "异常检测报告",
        "description": "对交易数据进行多维异常检测（高频交易、大额波动、关联交易等），输出异常清单。",
        "module": "risk_control",
        "params": {},
    },
    "case_3": {
        "id": "risk_case_3",
        "title": "综合风险评估 + 处置建议",
        "description": "生成完整风险评估报告：综合评分、风险等级、各维度指标、AI处置建议。POC演示推荐。",
        "module": "risk_control",
        "params": {},
    },
}

# ─── chatbi 演示用例 ─────────────────────────────────────

BI_CASES: dict = {
    "case_1": {
        "id": "bi_case_1",
        "title": "Top N 数据查询",
        "description": "按金额/数量排序，查询前10条业务数据。展示自然语言驱动的数据检索能力。",
        "module": "chatbi",
        "params": {"query": "按金额排序显示前10条记录", "table_name": ""},
    },
    "case_2": {
        "id": "bi_case_2",
        "title": "数据聚合分析",
        "description": "按类别分组统计总数/平均值，自动生成柱状图/饼图。展示数据智能分析能力。",
        "module": "chatbi",
        "params": {"query": "按类别统计总数并生成图表", "table_name": ""},
    },
    "case_3": {
        "id": "bi_case_3",
        "title": "条件筛选查询",
        "description": "带条件的精准数据查询（如：日期范围、金额阈值），展示自然语言条件过滤能力。",
        "module": "chatbi",
        "params": {"query": "查询近30天金额大于10000的记录", "table_name": ""},
    },
}

ALL_CASES = {**DOC_CASES, **FORECAST_CASES, **AGENT_CASES, **RISK_CASES, **BI_CASES}


def get_demo_cases(module: Optional[str] = None) -> list:
    """获取演示用例列表，可按模块筛选"""
    cases_list = []
    src = ALL_CASES
    for case_id, case in src.items():
        if module and case["module"] != module:
            continue
        cases_list.append(case)
    return cases_list


def execute_demo_case(case_id: str, industry_id: str) -> dict:
    """执行指定演示用例，返回结果"""
    case = ALL_CASES.get(case_id)
    if not case:
        return {"error": f"演示用例不存在: {case_id}"}

    module = case["module"]
    params = case["params"]
    ind = industry_id or settings.current_industry

    if module == "doc_parser":
        return _exec_doc_case(case_id, ind, params)
    elif module == "demand_forecast":
        return _exec_forecast_case(case_id, ind, params)
    elif module == "ai_agent":
        return _exec_agent_case(case_id, ind, params)
    elif module == "risk_control":
        return _exec_risk_case(case_id, ind, params)
    elif module == "chatbi":
        return _exec_bi_case(case_id, ind, params)
    return {"error": f"未知模块: {module}"}


def _exec_doc_case(case_id: str, industry_id: str, params: dict) -> dict:
    """执行文档解析演示用例"""
    from doc_parser.service import mock_parse, batch_parse_demo
    if case_id == "doc_case_1":
        cfg = get_doc_parser_config(industry_id)
        types = cfg.get("document_types", [])
        tid = types[0]["id"] if types else ""
        return mock_parse(industry_id, tid)
    elif case_id == "doc_case_2":
        return {"results": batch_parse_demo(industry_id), "total": len(batch_parse_demo(industry_id))}
    elif case_id == "doc_case_3":
        sample = params.get("sample_text", "")
        from doc_parser.service import _infer_doc_type, parse_with_llm
        inferred = _infer_doc_type(industry_id, sample)
        result = parse_with_llm(industry_id, inferred, sample)
        return {
            "case_title": "文档类型自动推断演示",
            "sample_text": sample,
            "inferred_type": inferred,
            "parse_result": result,
        }
    return {"error": "未知用例"}


def _exec_forecast_case(case_id: str, industry_id: str, params: dict) -> dict:
    """执行预测演示用例"""
    from demand_forecast.service import run_prediction, get_llm_insight
    periods = params.get("periods", 30)
    result = run_prediction(industry_id, periods)
    if params.get("insight"):
        result["insight"] = get_llm_insight(industry_id)
    return result


def _exec_agent_case(case_id: str, industry_id: str, params: dict) -> dict:
    """执行AI助手演示用例"""
    from ai_agent.service import chat, get_knowledge_base, batch_generate
    if case_id == "agent_case_1":
        msg = params.get("message", "请介绍一下当前行业的最新业务趋势和发展建议。")
        return chat(industry_id, msg)
    elif case_id == "agent_case_2":
        kb = get_knowledge_base(industry_id)
        items = kb.get("knowledge_base", [])
        matched = items[0] if items else {"question": "暂无知识库数据", "answer": "请配置知识库"}
        return {
            "matched_qa": matched,
            "knowledge_base": items[:5],
            "total": len(items),
        }
    elif case_id == "agent_case_3":
        company = params.get("company", "示例科技")
        marketing = batch_generate(industry_id, "marketing", {"company_name": company, "product": "企业AI智能中台", "target_market": "全行业"}, 3)
        invitation = batch_generate(industry_id, "invitation", {"company_name": company, "event_info": "2025企业数智化峰会"}, 3)
        return {"marketing": marketing.get("results", []), "invitation": invitation.get("results", [])}
    return {"error": "未知用例"}


def _exec_risk_case(case_id: str, industry_id: str, params: dict) -> dict:
    """执行风控演示用例"""
    from risk_control.service import analyze_transactions, detect_anomalies, assess_risk
    if case_id == "risk_case_1":
        return analyze_transactions(industry_id)
    elif case_id == "risk_case_2":
        return detect_anomalies(industry_id)
    elif case_id == "risk_case_3":
        tx = analyze_transactions(industry_id)
        ass = assess_risk(industry_id)
        return {"transaction_analysis": tx, "risk_assessment": ass}
    return {"error": "未知用例"}


def _exec_bi_case(case_id: str, industry_id: str, params: dict) -> dict:
    """执行BI演示用例"""
    from chatbi.service import query_data
    query = params.get("query", "显示所有数据")
    table = params.get("table_name", "")
    return query_data(industry_id, query, table)
