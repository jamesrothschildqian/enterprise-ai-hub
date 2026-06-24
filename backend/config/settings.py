"""
全局配置管理
通过 pydantic-settings 从 .env 和环境变量读取配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用基础配置
    app_name: str = "Enterprise AI Hub - 企业通用AI智能中台"
    debug: bool = True
    version: str = "2.0.0"

    # AI 供应商切换: "deepseek" | "openai" | "mock"
    ai_provider: str = "mock"

    # DeepSeek 配置
    deepseek_api_key: Optional[str] = ""
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # OpenAI 配置
    openai_api_key: Optional[str] = ""
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # 当前选中行业 (默认国际贸易)
    current_industry: str = "international_trade"

    # 文件上传大小限制 (MB)
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
