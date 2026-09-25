from services.embeddings.base_embedding import BaseEmbedding
from settings import settings


class OllamaEmbedding(BaseEmbedding):
    """Local Ollama embedding provider."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from ollama import Client
            self._client = Client(
                host=settings.OLLAMA_BASE_URL,
                timeout=30.0,
            )
        return self._client

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.embed(
            model=self.model_name,
            input=texts,
        )

        return response["embeddings"]