from settings import settings
import ollama
from services.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    """
    Ollama LLM implementation.
    """

    def __init__(
        self,
        model: str = settings.LLM_MODEL,
):
        self.model = model

    def invoke(
        self,
        prompt: str,
    ) -> str:

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]

    def health_check(
        self,
    ) -> dict:

        try:

            ollama.list()

            return {
                "status": "healthy",
                "model": self.model,
            }

        except Exception as e:

            return {
                "status": "unhealthy",
                "error": str(e),
            }
