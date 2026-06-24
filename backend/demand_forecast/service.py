"""
需求预测分析模块 - 业务逻辑层
提供简易时序预测算法 (移动平均+趋势外推)
支持6个行业各自独立的业务指标切换
"""
import math
from datetime import datetime, timedelta
from typing import List

from config.config_engine import get_forecast_config, get_forecast_mock
from utils.ai_llm import AILLM


def get_metrics(industry_id: str) -> list:
    """获取当前行业的所有预测指标定义"""
    cfg = get_forecast_config(industry_id)
    return cfg.get("metrics", [])


def get_history(industry_id: str) -> list:
    """获取当前行业的历史数据"""
    return get_forecast_mock(industry_id)


def _moving_average(data: List[float], window: int = 3) -> float:
    """简单移动平均"""
    if len(data) < window:
        return sum(data) / len(data) if data else 0
    return sum(data[-window:]) / window


def _calc_trend(data: List[float]) -> float:
    """计算趋势系数 (线性回归斜率)"""
    n = len(data)
    if n < 2:
        return 0
    x_avg = (n - 1) / 2
    y_avg = sum(data) / n
    num = sum((i - x_avg) * (data[i] - y_avg) for i in range(n))
    den = sum((i - x_avg) ** 2 for i in range(n))
    return num / den if den != 0 else 0


def _predict_next(history: List[float], periods: int = 30) -> List[float]:
    """
    预测未来N期的值
    算法: 加权移动平均 + 趋势调整
    """
    if not history:
        return []
    base = _moving_average(history, min(4, len(history)))
    trend = _calc_trend(history)
    # 衰减趋势系数，使远期预测趋于保守
    results = []
    for i in range(periods):
        trend_factor = trend * math.exp(-i / 15)
        seasonal = math.sin(i * 2 * math.pi / 12) * base * 0.05  # 简单季节因子
        val = base + trend_factor * (i + 1) + seasonal
        val = max(val, base * 0.6)  # 防止负值
        results.append(round(val, 2))
    return results


def run_prediction(industry_id: str, periods: int = 30) -> dict:
    """
    运行预测算法
    返回：各指标的历史+预测数据，已格式化为ECharts兼容结构
    """
    history = get_history(industry_id)
    metrics = get_metrics(industry_id)
    if not history or not metrics:
        return {"error": "无可用数据", "industry_id": industry_id}

    # 构造ECharts数据
    # X轴: 历史日期 + 预测日期标签
    last_date = datetime.strptime(history[-1]["date"], "%Y-%m-%d")
    dates = [h["date"] for h in history]
    pred_dates = []
    for i in range(1, periods + 1):
        d = last_date + timedelta(days=i)
        pred_dates.append(d.strftime("%Y-%m-%d"))

    series = []
    for metric in metrics:
        key = metric["key"]
        hist_values = [h.get(key, 0) for h in history]
        pred_values = _predict_next(hist_values, periods)

        series.append({
            "name": metric["name"],
            "key": key,
            "unit": metric.get("unit", ""),
            "history": [{"date": d, "value": v} for d, v in zip(dates, hist_values)],
            "prediction": [{"date": d, "value": v} for d, v in zip(pred_dates, pred_values)],
            "history_values": hist_values,
            "prediction_values": pred_values,
        })

    # ECharts line chart format
    echarts_data = {
        "xAxis": dates + pred_dates,
        "series": [
            {
                "name": s["name"],
                "type": "line",
                "smooth": True,
                "data": s["history_values"] + s["prediction_values"],
                "lineStyle": {"width": 2},
                "areaStyle": {"opacity": 0.1},
                "markLine": {
                    "data": [{"xAxis": dates[-1], "label": {"formatter": "当前"}}]
                },
            }
            for s in series
        ],
    }

    return {
        "industry_id": industry_id,
        "metrics": [{"name": s["name"], "key": s["key"], "unit": s.get("unit", "")} for s in series],
        "history_dates": dates,
        "prediction_dates": pred_dates,
        "series": series,
        "echarts": echarts_data,
        "algorithm": "加权移动平均 + 趋势外推 + 季节调整",
        "periods": periods,
        "confidence": round(0.85 - periods * 0.003, 2),  # 远期预测置信度递减
    }


def get_forecast_data(industry_id: str) -> dict:
    """获取完整的预测数据（含历史+初步预测）"""
    return run_prediction(industry_id, periods=30)


def get_llm_insight(industry_id: str, metric_key: str = "") -> str:
    """使用大模型生成预测洞察分析"""
    pred = run_prediction(industry_id, periods=30)
    if "error" in pred:
        return "暂无数据"

    series_info = []
    for s in pred["series"]:
        if metric_key and s["key"] != metric_key:
            continue
        hv = s["history_values"]
        pv = s["prediction_values"]
        series_info.append(
            f"{s['name']}: 历史均值{sum(hv)/len(hv):.1f}{s['unit']}, "
            f"末值{hv[-1]}, 预测均值{sum(pv)/len(pv):.1f}{s['unit']}"
        )

    llm = AILLM()
    msg = f"请分析以下业务指标预测数据，给出经营建议：\n" + "\n".join(series_info)
    result = llm.chat([{"role": "user", "content": msg}])
    return result
