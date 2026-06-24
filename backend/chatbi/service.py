"""
智能数据问答(自然语言BI)模块 - 业务逻辑层
用户输入自然语言，大模型生成查询逻辑，返回结构化图表数据
"""
import json
import re
from typing import Optional

from config.config_engine import get_chatbi_config, get_chatbi_mock
from utils.ai_llm import AILLM


def get_tables(industry_id: str) -> dict:
    """获取当前行业所有可用的数据表（含表结构和预览数据）"""
    tables_cfg = get_chatbi_config(industry_id)
    table_schemas = tables_cfg.get("table_schemas", [])
    mock_tables = get_chatbi_mock(industry_id)
    result = []
    for schema in table_schemas:
        name = schema["name"]
        rows = mock_tables.get(name, [])
        result.append({
            "name": name,
            "columns": schema.get("columns", []),
            "primary_key": schema.get("primary_key", ""),
            "row_count": len(rows),
            "preview": rows[:3] if rows else [],
        })
    return {"industry_id": industry_id, "tables": result}


def query_data(industry_id: str, query_text: str, table_name: str = "") -> dict:
    """
    自然语言查询接口
    1. 用户输入自然语言问句
    2. 大模型生成查询逻辑（表名/筛选条件/聚合方式）
    3. 在Mock数据上执行查询
    4. 返回表格数据+图表配置
    """
    tables_cfg = get_chatbi_config(industry_id)
    mock_tables = get_chatbi_mock(industry_id)
    query_prompt_tpl = tables_cfg.get(
        "query_prompt",
        "你是一位数据分析师。用户问：{user_query}\n可用的数据表：{tables}\n请生成JSON查询逻辑。",
    )

    # 准备表信息
    table_schemas = tables_cfg.get("table_schemas", [])
    tables_info = []
    for ts in table_schemas:
        tables_info.append(f"表名: {ts['name']}, 字段: {', '.join(ts['columns'])}")
    tables_str = "\n".join(tables_info)

    # 生成查询逻辑
    query_prompt = query_prompt_tpl.replace("{user_query}", query_text).replace("{tables}", tables_str)
    llm = AILLM()
    query_logic = llm.chat_with_json([
        {"role": "system", "content": "你是一个数据分析师。根据用户的问题和数据表结构，生成数据查询JSON。"},
        {"role": "user", "content": query_prompt},
    ])

    # 执行查询（在Mock数据上模拟）
    return _execute_query(query_text, query_logic, mock_tables, table_schemas, table_name)


def _execute_query(
    query_text: str,
    query_logic: dict,
    mock_tables: dict,
    table_schemas: list,
    table_name: str = "",
) -> dict:
    """在Mock数据上模拟执行查询"""
    # 确定目标表
    target_table = table_name
    if not target_table:
        target_table = query_logic.get("table_name", "")
    if not target_table and table_schemas:
        target_table = table_schemas[0]["name"]
    if not target_table or target_table not in mock_tables:
        target_table = next(iter(mock_tables.keys()), "")
    if not target_table:
        return {"error": "无可用数据表", "query": query_text}

    rows = mock_tables[target_table]
    schema = next((s for s in table_schemas if s["name"] == target_table), None)
    columns = schema["columns"] if schema else (list(rows[0].keys()) if rows else [])

    # 过滤（简易实现）
    filtered = rows
    filter_info = query_logic.get("filter") or query_logic.get("filters", {})
    if isinstance(filter_info, dict) and filter_info.get("field"):
        field = filter_info["field"]
        value = filter_info.get("value", "")
        filtered = [r for r in filtered if str(r.get(field, "")).find(str(value)) >= 0]

    # 排序
    order_by = query_logic.get("order_by") or query_logic.get("sort", "")
    if order_by:
        desc = query_logic.get("desc", False)
        filtered = sorted(
            filtered,
            key=lambda r: _safe_num(r.get(order_by, 0)),
            reverse=desc,
        )

    # 限制条数
    limit = query_logic.get("limit", 20)
    if isinstance(limit, (int, float)):
        filtered = filtered[:int(limit)]

    # Aggregation
    agg = query_logic.get("aggregation", "")
    group_by = query_logic.get("group_by", "")
    agg_result = None
    if agg and group_by and filtered:
        groups = {}
        for r in filtered:
            g_key = str(r.get(group_by, "未知"))
            if g_key not in groups:
                groups[g_key] = []
            groups[g_key].append(r)
        agg_result = {}
        for g, items in groups.items():
            values = [_safe_num(i.get(agg, 0)) for i in items]
            agg_result[g] = round(sum(values), 2)

    # 构造图表数据
    chart = _build_chart(query_text, filtered, columns, schema)

    return {
        "query": query_text,
        "table_name": target_table,
        "columns": columns,
        "rows": filtered,
        "total_rows": len(filtered),
        "aggregation": agg_result,
        "sql": _generate_sql(target_table, columns, filter_info, order_by, limit),
        "chart": chart,
        "summary": _generate_summary(query_text, target_table, len(filtered), chart),
    }


def _build_chart(query: str, rows: list, columns: list, schema: dict) -> Optional[dict]:
    """根据查询内容和数据自动推荐图表"""
    if not rows or len(columns) < 2:
        return None

    # 找数值列和类别列
    numeric_cols = []
    category_cols = []
    for col in columns:
        vals = [r.get(col) for r in rows[:5] if r.get(col) is not None]
        if vals and all(isinstance(v, (int, float)) for v in vals):
            numeric_cols.append(col)
        else:
            category_cols.append(col)

    if not numeric_cols or not category_cols:
        numeric_cols = [c for c in columns if c != columns[0]]
        category_cols = [columns[0]]

    chart_type = "bar"
    if "趋势" in query or "趋势" in query or "变化" in query:
        chart_type = "line"
    elif "占比" in query or "比例" in query or "分布" in query:
        chart_type = "pie"

    return {
        "chart_type": chart_type,
        "title": f"{category_cols[0]} vs {numeric_cols[0]}",
        "x_axis": category_cols[0],
        "y_axis": numeric_cols[0],
        "data": [
            {"name": str(r.get(category_cols[0], "")), "value": _safe_num(r.get(numeric_cols[0], 0))}
            for r in rows[:20]
        ],
    }


def _generate_sql(table: str, columns: list, filter_info: dict, order: str, limit) -> str:
    """生成模拟SQL"""
    cols = ", ".join(columns[:10])
    sql = f"SELECT {cols} FROM {table}"
    if filter_info and isinstance(filter_info, dict) and filter_info.get("field"):
        sql += f" WHERE {filter_info['field']} LIKE '%{filter_info.get('value', '')}%'"
    if order:
        sql += f" ORDER BY {order}"
    if limit:
        sql += f" LIMIT {limit}"
    return sql


def _generate_summary(query: str, table: str, row_count: int, chart: Optional[dict]) -> str:
    """生成自然语言摘要"""
    parts = [f"在【{table}】表中查询到 {row_count} 条记录。"]
    if chart:
        parts.append(f"推荐{chart['chart_type']}图展示{chart['x_axis']}与{chart['y_axis']}的关系。")
    return " ".join(parts)


def _safe_num(v) -> float:
    """安全转为数字"""
    try:
        return float(v) if v else 0
    except (ValueError, TypeError):
        return 0
