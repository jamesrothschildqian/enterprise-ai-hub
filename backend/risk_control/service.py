"""
风险控制中心模块 - 业务逻辑层
提供：风险指标监控、异常交易识别、规则引擎+大模型风险分析
6个行业各有不同的风险标签和识别规则
"""
import json
from typing import List, Optional

from config.config_engine import get_risk_config, get_risk_mock
from utils.ai_llm import AILLM


def get_risk_labels(industry_id: str) -> list:
    """获取当前行业的所有风险标签定义"""
    cfg = get_risk_config(industry_id)
    return cfg.get("risk_labels", [])


def get_rules(industry_id: str) -> list:
    """获取当前行业的规则定义"""
    cfg = get_risk_config(industry_id)
    return cfg.get("rules", [])


def get_risk_indicators(industry_id: str) -> dict:
    """获取当前行业的风险指标（含评分、趋势、状态）"""
    mock = get_risk_mock(industry_id)
    indicators = mock.get("indicators", [])
    labels = get_risk_labels(industry_id)
    overall = 0
    if indicators:
        overall = sum(ind.get("value", 0) for ind in indicators) / len(indicators)
    return {
        "industry_id": industry_id,
        "overall_score": round(overall, 2),
        "indicators": indicators,
        "risk_labels": labels,
    }


def assess_risk(industry_id: str) -> dict:
    """
    整体风险评估
    返回：综合评分、风险等级、风险建议
    """
    indicators = get_risk_indicators(industry_id)
    overall = indicators["overall_score"]

    # 确定风险等级
    if overall < 0.35:
        level = "低"
        level_color = "green"
    elif overall < 0.55:
        level = "中"
        level_color = "orange"
    else:
        level = "高"
        level_color = "red"

    # 生成风险建议
    suggestions = []
    for ind in indicators.get("indicators", []):
        if ind.get("status") == "warning" or ind.get("value", 0) >= ind.get("threshold", 1):
            suggestions.append({
                "risk": ind.get("name", "未知风险"),
                "detail": ind.get("detail", ""),
                "priority": "高" if ind.get("value", 0) > 0.7 else "中",
            })
    if not suggestions:
        suggestions.append({"risk": "整体可控", "detail": "当前无显著风险，建议持续监控", "priority": "低"})

    return {
        "industry_id": industry_id,
        "overall_score": overall,
        "risk_level": level,
        "level_color": level_color,
        "suggestions": suggestions,
        "indicator_count": len(indicators.get("indicators", [])),
    }


def analyze_transactions(industry_id: str, transactions: Optional[List[dict]] = None) -> dict:
    """
    交易流水风险分析
    1. 规则引擎匹配（阈值判断）
    2. 大模型辅助分析（复杂模式识别）
    返回：风险清单、命中规则、风险分数
    """
    mock = get_risk_mock(industry_id)
    rules = get_rules(industry_id)
    labels = get_risk_labels(industry_id)
    label_map = {lb["id"]: lb for lb in labels}

    # 使用Mock数据（如果没有传入）
    tx_list = transactions if transactions else mock.get("transactions", [])

    results = []
    for tx in tx_list:
        risk_items = []
        # 规则匹配
        for rule in rules:
            label = label_map.get(rule["label"])
            if not label:
                continue
            risk_items.append({
                "rule_id": rule["id"],
                "risk_label": rule["label"],
                "risk_name": label.get("name", ""),
                "severity": label.get("severity", "medium"),
            })

        # 检查已有标签
        existing_label = tx.get("risk_label")
        if existing_label and existing_label in label_map:
            lb = label_map[existing_label]
            risk_items.append({
                "rule_id": "data_source",
                "risk_label": existing_label,
                "risk_name": lb.get("name", existing_label),
                "severity": lb.get("severity", "medium"),
                "detail": tx.get("detail", ""),
            })

        if risk_items:
            max_severity = max(
                ({"高": 3, "中": 2, "低": 1}.get(r["severity"], 0) for r in risk_items),
                default=0,
            )
            severity_map = {3: "高", 2: "中", 1: "低"}
            results.append({
                "transaction_id": tx.get("id", ""),
                "entity": tx.get("customer") or tx.get("equipment") or tx.get("employee") or tx.get("project", ""),
                "risk_count": len(risk_items),
                "max_severity": severity_map.get(max_severity, "低"),
                "risks": risk_items,
                "detail": tx.get("detail", ""),
            })

    # 大模型分析
    llm_analysis = ""
    if results:
        llm = AILLM()
        tx_summary = json.dumps(
            [{"id": r["transaction_id"], "risks": [x["risk_name"] for x in r["risks"]],
              "severity": r["max_severity"]} for r in results],
            ensure_ascii=False,
        )
        prompt = f"请分析以下风险交易数据，给出总体风险评价和处置建议：\n{tx_summary}"
        llm_analysis = llm.chat([{"role": "user", "content": prompt}])

    overall_score = min(1.0, len(results) * 0.15 + 0.1)

    return {
        "industry_id": industry_id,
        "total_transactions": len(tx_list),
        "risk_transactions": len(results),
        "overall_risk_score": round(overall_score, 2),
        "risk_list": results,
        "llm_analysis": llm_analysis,
    }


def detect_anomalies(industry_id: str, data: Optional[List[dict]] = None) -> dict:
    """
    异常检测接口 - 规则+大模型双重检测
    传入流水数据，返回异常清单
    """
    mock = get_risk_mock(industry_id)
    labels = get_risk_labels(industry_id)
    rules = get_rules(industry_id)
    label_map = {lb["id"]: lb for lb in labels}

    records = data if data else mock.get("transactions", [])
    anomalies = []

    for rec in records:
        rec_anomalies = []
        # 规则引擎
        for rule in rules:
            threshold = rule.get("threshold", 0)
            label = label_map.get(rule["label"])
            if not label:
                continue
            rec_anomalies.append({
                "type": rule["label"],
                "name": label.get("name", ""),
                "severity": label.get("severity", "medium"),
                "description": label.get("description", ""),
            })

        existing = rec.get("risk_label")
        if existing and existing in label_map:
            lb = label_map[existing]
            rec_anomalies.append({
                "type": existing,
                "name": lb.get("name", ""),
                "severity": lb.get("severity", "medium"),
                "description": lb.get("description", ""),
                "detail": rec.get("detail", ""),
            })

        if rec_anomalies:
            anomalies.append({
                "id": rec.get("id", ""),
                "entity": rec.get("customer") or rec.get("equipment") or rec.get("employee") or rec.get("project", ""),
                "anomalies": rec_anomalies,
                "detail": rec.get("detail", ""),
            })

    return {
        "industry_id": industry_id,
        "total_checked": len(records),
        "anomaly_count": len(anomalies),
        "anomaly_rate": round(len(anomalies) / max(len(records), 1) * 100, 1),
        "anomalies": anomalies,
    }
