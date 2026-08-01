"""DeepSeek API 封装

统一处理重试、超时、错误恢复，对外暴露简单的 annotate_10k() 接口。
"""

import json
import os
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .prompts import build_annotation_prompt


class DeepSeekClient:
    """DeepSeek API 客户端，用于 10-K 智能标注。"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is required. "
                "Set DEEPSEEK_API_KEY environment variable or pass api_key parameter."
            )
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def annotate(
        self,
        candidates: list[dict],
        company: dict,
        temperature: float = 0.2,
    ) -> dict:
        """调用 DeepSeek 完成候选段落的智能标注。

        Args:
            candidates: text_locator.locate_candidates() 的输出
            company: {"ticker": str, "fiscal_year": int, "industry": str}
            temperature:  creativity temperature (低=保守，高=发散)

        Returns:
            DeepSeek 返回的 JSON dict（已解析），包含 risk_signals, dimension_scores 等
        """
        prompt = build_annotation_prompt(candidates, company)

        resp = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a forensic accounting AI assistant. "
                            "You must not invent text or hallucinate numbers. "
                            "Every excerpt must be verbatim from the input. "
                            "Output strictly valid JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": 4000,
                "response_format": {"type": "json_object"},
            },
            timeout=120,
        )
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"]
        # 保险：有时 content 可能被 markdown 代码块包裹
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)

    def health_check(self) -> bool:
        """简单的连通性检查。"""
        try:
            resp = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Say OK"}],
                    "max_tokens": 10,
                },
                timeout=15,
            )
            return resp.status_code == 200
        except Exception:
            return False
