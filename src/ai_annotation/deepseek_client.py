"""DeepSeek API 封装

统一处理重试、超时、错误恢复，对外暴露简单的 annotate() 接口。
支持中英文切换（美股10-K / A股年报）。
v4.5: 增加 .env 文件自动加载
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# v4.5: 自动加载 .env 文件
REPO_ROOT = Path(__file__).parent.parent.parent
env_path = REPO_ROOT / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

from .cn_prompts import CN_SYSTEM_PROMPT, build_cn_annotation_prompt
from .prompts import build_annotation_prompt


class DeepSeekClient:
    """DeepSeek API 客户端，用于年报智能标注。"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is required. "
                "Set DEEPSEEK_API_KEY environment variable, create .env file, or pass api_key parameter."
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
        language: str = "en",
    ) -> dict:
        """调用 DeepSeek 完成候选段落的智能标注。"""
        if language == "cn":
            prompt = build_cn_annotation_prompt(candidates, company)
            system_content = CN_SYSTEM_PROMPT
        else:
            prompt = build_annotation_prompt(candidates, company)
            system_content = (
                "You are a forensic accounting AI assistant. "
                "You must not invent text or hallucinate numbers. "
                "Every excerpt must be verbatim from the input. "
                "Output strictly valid JSON only."
            )

        resp = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": 8000,
                "response_format": {"type": "json_object"},
            },
            timeout=180,
        )
        resp.raise_for_status()

        try:
            resp_payload = resp.json()
        except json.JSONDecodeError as e:
            raw_text = resp.text[:2000]
            raise RuntimeError(
                f"DeepSeek API 返回的不是合法 JSON。"
                f"HTTP 状态: {resp.status_code}。"
                f"原始响应前 2000 字符:\n{raw_text}"
            ) from e

        if "error" in resp_payload:
            raise RuntimeError(
                f"DeepSeek API 返回错误: {resp_payload['error']}"
            )

        choices = resp_payload.get("choices", [])
        if not choices:
            raise RuntimeError(
                f"DeepSeek API 返回的 choices 为空。完整响应:\n{json.dumps(resp_payload, indent=2, ensure_ascii=False)}"
            )

        msg = choices[0]["message"]
        content = msg.get("content", "")

        if not content or not content.strip():
            raise RuntimeError(
                f"DeepSeek API 返回的 content 为空。"
                f"完整响应:\n{json.dumps(resp_payload, indent=2, ensure_ascii=False)}"
            )

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"DeepSeek 返回的 content 不是合法 JSON。"
                f"模型: {self.model}。"
                f"解析失败内容前 2000 字符:\n{content[:2000]}"
            ) from e

    def health_check(self) -> bool:
        """简单的连通性检查，失败时打印详细错误。"""
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
            if resp.status_code != 200:
                print(f"[health_check] HTTP {resp.status_code}: {resp.text[:500]}")
                return False
            try:
                resp.json()
                return True
            except Exception as e:
                print(f"[health_check] JSON 解析失败: {e}")
                return False
        except Exception as e:
            print(f"[health_check] 请求异常: {e}")
            return False
