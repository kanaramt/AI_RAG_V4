from settings import settings
from services.llm.ollama_llm import OllamaLLM


class LLMFactory:
    """
    Factory for creating LLM providers for health checking.
    """

    @staticmethod
    def create():
        provider = (settings.LLM_PROVIDER or "ollama").lower()
        if provider == "ollama":
            return OllamaLLM()

        class CloudLLMHealth:
            def health_check(self):
                return {"status": "healthy", "provider": provider, "message": f"{provider} provider active"}

        return CloudLLMHealth()
