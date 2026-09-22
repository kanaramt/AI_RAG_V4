from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class BaseLLMProvider(ABC):
    """
    Base interface for all LLM providers.

    Every provider (Ollama, OpenAI, Gemini,
    Claude, Grok, etc.) must implement
    these methods.
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        Generate a response.
        """
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Stream tokens.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check whether the provider
        is available.
        """
        pass
