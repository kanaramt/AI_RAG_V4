import os
import httpx

from services.embeddings.base_embedding import BaseEmbedding


class GeminiEmbedding(BaseEmbedding):
    """Direct Google Gemini embedding provider."""

    def __init__(self, model_name: str, api_key: str | None = None):
        self.model_name = model_name
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if not self.api_key:
            raise RuntimeError(
                f"Gemini API key is required for embedding model "
                f"'{self.model_name}'."
            )

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model_name}:embedContent"
        )

        embeddings = []

        for text in texts:
            response = httpx.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key,
                },
                json={
                    "model": f"models/{self.model_name}",
                    "content": {
                        "parts": [
                            {"text": text}
                        ]
                    }
                },
                timeout=60.0,
            )

            response.raise_for_status()

            embedding = response.json()["embedding"]["values"]
            embeddings.append(embedding)

        return embeddings