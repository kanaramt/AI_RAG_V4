from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """
    Base interface for all LLM providers.
    """

    @abstractmethod
    def invoke(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response for a prompt.
        """
        pass

    @abstractmethod
    def health_check(
        self,
    ) -> dict:
        """
        Verify the model is available.
        """
        pass
