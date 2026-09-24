import os
from typing import Any, AsyncGenerator

from llm.config import LLMConfig
from llm.providers.base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """
    Anthropic Claude LLM Provider using AsyncAnthropic.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model
        self.api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = config.base_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        temp = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        
        system_prompt = None
        cleaned_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content")
            else:
                cleaned_messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content")
                })
        print(f"[CLAUDE] Model={self.model}")
        print(f"[CLAUDE] Messages={len(cleaned_messages)}")

        create_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": cleaned_messages,
            "system": system_prompt,
            "max_tokens": max_tokens,
        }

        # Anthropic rules: omit temperature parameter for Opus 4.7+ and next-gen reasoning models
        m_lower = self.model.lower()
        is_fixed_temp_model = any(k in m_lower for k in [
            "claude-opus-4-7",
            "claude-opus-4-8",
            "claude-opus-5",
            "claude-sonnet-5",
        ])
        if not is_fixed_temp_model and temp is not None:
            create_kwargs["temperature"] = temp
        
        response = await self.client.messages.create(**create_kwargs)
        print("[CLAUDE] Response received")
        print(f"[CLAUDE] Response={response.content[0].text}")
        return response.content[0].text if response.content else ""

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        temp = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)

        system_prompt = None
        cleaned_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content")
            else:
                cleaned_messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content")
                })

        stream_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": cleaned_messages,
            "system": system_prompt,
            "max_tokens": max_tokens,
        }

        m_lower = self.model.lower()
        is_fixed_temp_model = any(k in m_lower for k in [
            "claude-opus-4-7",
            "claude-opus-4-8",
            "claude-opus-5",
            "claude-sonnet-5",
        ])
        if not is_fixed_temp_model and temp is not None:
            stream_kwargs["temperature"] = temp

        async with self.client.messages.stream(**stream_kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def health_check(self) -> bool:
        return bool(self.api_key)
