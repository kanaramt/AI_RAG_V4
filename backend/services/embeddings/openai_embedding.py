import os
import httpx

from services.embeddings.base_embedding import BaseEmbedding


class OpenAIEmbedding(BaseEmbedding):
    """Direct OpenAI Embeddings API provider."""

    def __init__(self, model_name: str, api_key: str | None = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key is required for embedding model "
                f"'{self.model_name}'."
            )

        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model_name,
                "input": texts,
            },
            timeout=60.0,
        )

        response.raise_for_status()

        data = response.json()["data"]

        data.sort(key=lambda item: item["index"])

        return [item["embedding"] for item in data]