"""
Enterprise AI Hub - 企业通用AI智能中台
FastAPI 主入口
功能：CORS跨域、路由注册、全局配置引擎、Swagger文档
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.config_engine import get_all_industries, reload as reload_config, set_lang

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    # Enterprise AI Hub · 企业通用AI智能中台
    
    ## 轻量化PoC项目 - 通用型企业AI中台Demo
    
    ### 核心特性
    - **6大行业一键切换**: 国际贸易/智能制造/金融/航运物流/房地产/HR人力资源
    - **5大业务模块**: 文档智能解析/需求预测/AI助手/风险控制/智能数据问答
    - **零数据库依赖**: 所有数据以JSON文件存储于 config/mock_data/
    - **AI双模型切换**: DeepSeek / OpenAI / Mock 三种模式
    - **完整Swagger文档**: 所有接口均包含详细说明和请求/响应示例
    
    ### 快速开始
    1. 启动后端: `python main.py` → 访问 http://localhost:8000
    2. 查看文档: http://localhost:8000/docs
    3. 前端访问: http://localhost:3000 (需先启动前端)
    
    ### 行业切换
    - 修改 `config/settings.py` 中的 `current_industry` 或通过API `/api/industry/switch`
    - 所有模块自动切换数据源和配置
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 跨域配置 - 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 语言中间件 ─────────────────────────────────────────
# 从请求 Query String 中读取 ?lang=en/zh，全局设置 config_engine 语言


@app.middleware("http")
async def lang_middleware(request: Request, call_next):
    lang = request.query_params.get("lang", "en")
    set_lang(lang)
    response = await call_next(request)
    return response


# ─── 全局行业路由 ───────────────────────────────────────


@app.get("/api/industries", tags=["全局 / Global"])
def api_get_industries():
    """获取所有行业列表（供前端下拉框使用）"""
    return {"industries": get_all_industries()}


@app.get("/api/industry/{industry_id}", tags=["全局 / Global"])
def api_get_industry(industry_id: str):
    """获取指定行业的完整配置和数据"""
    from config.config_engine import get_industry_basic, get_doc_parser_config, \
        get_forecast_config, get_ai_agent_config, get_risk_config, get_chatbi_config
    return {
        "industry_id": industry_id,
        "basic": get_industry_basic(industry_id),
        "config": {
            "doc_parser": get_doc_parser_config(industry_id),
            "demand_forecast": get_forecast_config(industry_id),
            "ai_agent": get_ai_agent_config(industry_id),
            "risk_control": get_risk_config(industry_id),
            "chatbi": get_chatbi_config(industry_id),
        },
    }


@app.post("/api/industry/switch", tags=["全局 / Global"])
def api_switch_industry(body: dict):
    """切换当前行业"""
    industry_id = body.get("industry_id", "")
    all_ids = [ind["id"] for ind in get_all_industries()]
    if industry_id in all_ids:
        settings.current_industry = industry_id
        return {"status": "ok", "current_industry": industry_id, "message": f"已切换至 {industry_id}"}
    return {"error": f"无效行业ID: {industry_id}，可选: {', '.join(all_ids)}"}


@app.get("/api/health", tags=["全局 / Global"])
def api_health():
    """健康检查接口"""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "current_industry": settings.current_industry,
        "ai_provider": settings.ai_provider,
    }


# ─── 注册5大业务模块路由 ──────────────────────────────

from doc_parser.router import router as doc_parser_router
from demand_forecast.router import router as demand_forecast_router
from ai_agent.router import router as ai_agent_router
from risk_control.router import router as risk_control_router
from chatbi.router import router as chatbi_router
from services.demo_router import router as demo_router
from report_generator.router import router as report_router

app.include_router(doc_parser_router, prefix="/api/doc-parser")
app.include_router(demand_forecast_router, prefix="/api/demand-forecast")
app.include_router(ai_agent_router, prefix="/api/ai-agent")
app.include_router(risk_control_router, prefix="/api/risk-control")
app.include_router(chatbi_router, prefix="/api/chatbi")
app.include_router(demo_router, prefix="/api/demo")
app.include_router(report_router, prefix="/api/report")


if __name__ == "__main__":
    import uvicorn
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║     Enterprise AI Hub · v{settings.version}      ║
    ║  企业通用AI智能中台  演示模式: {settings.ai_provider.upper():8s}  ║
    ╠══════════════════════════════════════════════╣
    ║  Swagger 文档: http://localhost:8000/docs    ║
    ║  ReDoc 文档:  http://localhost:8000/redoc    ║
    ║  当前行业:     {settings.current_industry:30s}  ║
    ╚══════════════════════════════════════════════╝
    """)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
