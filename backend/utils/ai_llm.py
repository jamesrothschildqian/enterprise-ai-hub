"""
统一AI大模型调用工具类
支持 DeepSeek / OpenAI / Mock 三种模式一键切换
所有模块通过此工具类调用AI能力，无需关心底层实现
"""
import json
import random
from typing import Optional, List, Dict
from openai import OpenAI as OpenAIClient
from config.settings import settings


class AILLM:
    """
    AI大模型统一调用封装
    支持 provider: "deepseek" | "openai" | "mock"
    使用方式：
        llm = AILLM()
        reply = llm.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.ai_provider
        self._client = None

    def _get_client(self):
        """懒加载获取API客户端"""
        if self._client is not None:
            return self._client
        if self.provider == "deepseek":
            self._client = OpenAIClient(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_api_base,
            )
        elif self.provider == "openai":
            self._client = OpenAIClient(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base,
            )
        return self._client

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: Optional[str] = None,
    ) -> str:
        """
        统一对话接口
        Args:
            messages: 对话消息列表 [{"role": "user"/"assistant"/"system", "content": "..."}]
            temperature: 生成温度 (0-1)
            max_tokens: 最大生成token数
            model: 指定模型名，为空则使用配置的默认模型
        Returns:
            模型回复文本
        """
        if self.provider == "mock" or not self._has_api_key():
            return self._mock_reply(messages)

        try:
            client = self._get_client()
            model_name = model or (
                settings.deepseek_model if self.provider == "deepseek"
                else settings.openai_model
            )
            resp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[AI服务调用失败，降级为Mock回复] 错误：{str(e)}\n\n{self._mock_reply(messages)}"

    def chat_with_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
    ) -> dict:
        """
        对话并以JSON格式返回结果 (强制JSON模式)
        """
        raw = self.chat(messages, temperature=temperature)
        try:
            # 尝试从回复中提取JSON
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw[start:end + 1])
            return json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            return {"raw_response": raw, "error": "AI回复不是合法JSON格式"}

    def switch_provider(self, provider: str):
        """运行时切换AI供应商"""
        self.provider = provider
        self._client = None

    def _has_api_key(self) -> bool:
        """检查是否有可用的API密钥"""
        if self.provider == "deepseek":
            return bool(settings.deepseek_api_key) and settings.deepseek_api_key != "your_deepseek_api_key_here"
        elif self.provider == "openai":
            return bool(settings.openai_api_key) and settings.openai_api_key != "your_openai_api_key_here"
        return False

    def _mock_reply(self, messages: List[Dict[str, str]]) -> str:
        """
        Mock模式回复 - 无需API密钥即可返回模拟回复
        用于PoC演示和开发调试
        """
        last_msg = messages[-1]["content"] if messages else ""
        msg_lower = last_msg.lower()

        # 提取字段类请求
        if "提取" in last_msg or "json" in msg_lower or "结构化" in last_msg:
            return json.dumps({"status": "mock_parsed", "message": "Mock模式下模拟的字段提取结果，字段数量: 8", "fields_count": 8}, ensure_ascii=False)

        # 预测类请求
        if "预测" in last_msg or "趋势" in last_msg or "forecast" in msg_lower:
            return json.dumps({
                "prediction": [random.uniform(100, 200) for _ in range(7)],
                "trend": "up" if random.random() > 0.5 else "down",
                "confidence": round(random.uniform(0.7, 0.95), 2),
            }, ensure_ascii=False)

        # 风险分析类
        if "风险" in last_msg or "异常" in last_msg or "风险" in last_msg:
            risks = ["回款逾期", "货损风险", "合规违规", "质量缺陷", "供应中断"]
            selected = random.sample(risks, k=min(3, len(risks)))
            return json.dumps({
                "risks": [{"label": r, "level": random.choice(["低", "中", "高"]), "score": round(random.uniform(0.3, 0.9), 2)} for r in selected],
                "overall_risk": round(random.uniform(0.3, 0.7), 2),
            }, ensure_ascii=False)

        # BI查询类
        if "查询" in last_msg or "数据" in last_msg or "table" in msg_lower:
            return json.dumps({
                "table_name": "mock_table",
                "filter": {"field": "date", "operator": ">=", "value": "2024-01-01"},
                "aggregation": "sum",
                "group_by": "category",
            }, ensure_ascii=False)

        # 文案生成类
        if "文案" in last_msg or "营销" in last_msg or "邀约" in last_msg:
            return f"""尊敬的客户：

您好！感谢您长期以来对我们公司的支持与信任。我们诚挚地邀请您参加即将举办的行业交流活动。

活动亮点：
1. 行业专家深度分享
2. 最新产品与技术展示
3. 商务合作洽谈机会

期待您的莅临！

此致
敬礼
[AI自动生成·Mock模式]"""

        # 默认回复
        industry_knowledge = [
            "根据行业最佳实践，建议从流程标准化、数据驱动决策、持续改进三个维度推进数字化转型。",
            "针对您提出的问题，建议参考以下方案：1. 明确业务目标与KPI；2. 梳理核心业务流程；3. 选择合适的技术工具；4. 建立持续优化机制。",
            "这是一个很好的问题。从行业数据来看，采用AI技术后，企业平均运营效率提升25-35%，风险识别准确率提高40%以上。",
            "建议您先进行现状诊断，识别关键瓶颈点，然后制定分阶段实施计划。初期可从投入产出比最高的场景切入。",
        ]
        return f"您好！我是Enterprise AI Hub智能助手。\n\n{random.choice(industry_knowledge)}\n\n(当前为Mock演示模式，配置API_KEY后可获取更精准的AI回复)"
