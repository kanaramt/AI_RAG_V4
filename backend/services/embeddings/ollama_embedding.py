from services.embeddings.base_embedding import BaseEmbedding
from services.embedding_service import EmbeddingService


class OllamaEmbedding(BaseEmbedding):
    """
    Ollama embedding provider.

    Uses the existing EmbeddingService internally.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def generate_embedding(
        self,
        text: str,
    ) -> list[float]:

        return self.embedding_service.generate_embedding(text)

    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return self.embedding_service.generate_embeddings(texts)
