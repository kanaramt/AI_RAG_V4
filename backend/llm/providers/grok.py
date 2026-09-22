import os
import json
import httpx
from typing import Any, AsyncGenerator

from llm.config import LLMConfig
from llm.providers.base import BaseLLMProvider


class GrokProvider(BaseLLMProvider):
    """
    xAI Grok LLM Provider (https://api.x.ai/v1).
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model or "grok-beta"
        self.api_key = config.api_key or os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
        self.base_url = config.base_url or "https://api.x.ai/v1"

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        if not self.api_key:
            raise ValueError("GROK_API_KEY or XAI_API_KEY is not set. Please add your Grok API key in Settings -> API Keys & Cloud LLMs.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.config.temperature or 0.2,
            "stream": False
        }

        url = f"{self.base_url.rstrip('/')}/chat/completions"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Grok API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        full_text = await self.chat(messages, **kwargs)
        yield full_text

    async def health_check(self) -> bool:
        return bool(self.api_key)
