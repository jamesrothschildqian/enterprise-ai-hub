"""
智能数据问答(自然语言BI)模块 - API路由
提供：数据表查询、自然语言查询、图表数据
"""
from typing import Optional
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from chatbi.service import get_tables, query_data
from config.settings import settings

router = APIRouter(tags=["智能数据问答 / ChatBI"])


class QueryRequest(BaseModel):
    query: str = Body(..., description="自然语言查询，如：'按金额排序显示前5条'")
    table_name: str = Body("", description="指定数据表名，为空则自动选择")
    industry_id: Optional[str] = Body(None, description="行业ID")


@router.get(
    "/tables",
    summary="获取数据表列表",
    description="返回当前行业的所有数据表定义，包含表名、字段列表、主键、记录数和预览数据",
)
def api_tables(
    industry_id: Optional[str] = Query(None, description="行业ID"),
):
    ind = industry_id or settings.current_industry
    return get_tables(ind)


@router.post(
    "/query",
    summary="自然语言查询",
    description="用户输入自然语言问句，大模型自动生成查询逻辑并返回结果<br>"
                "返回：表格数据、图表配置(echarts)、模拟SQL、自然语言摘要<br>"
                "示例：'按金额排序显示前10条客户订单'",
)
def api_query(req: QueryRequest):
    ind = req.industry_id or settings.current_industry
    return query_data(ind, req.query, req.table_name)
