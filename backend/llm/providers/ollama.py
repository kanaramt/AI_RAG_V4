from typing import Any, AsyncGenerator

from llm.providers.base import BaseLLMProvider
from llm.config import LLMConfig


class OllamaProvider(BaseLLMProvider):
    """
    Ollama LLM Provider.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from ollama import AsyncClient
            self._client = AsyncClient(
                host=self.config.base_url or "http://localhost:11434",
                timeout=300.0
            )
        return self._client

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        Generate a complete response.
        """

        response = await self.client.chat(
            model=self.model,
            messages=messages,
        )

        return response["message"]["content"]

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Stream the response token-by-token.
        """

        async for chunk in await self.client.chat(
            model=self.model,
            messages=messages,
            stream=True,
        ):
            yield chunk["message"]["content"]

    async def health_check(self) -> bool:
        """
        Check if Ollama is reachable.
        """

        try:
            await self.client.ps()
            return True

        except Exception:
            return False
