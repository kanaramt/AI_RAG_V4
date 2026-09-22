from services.embeddings.base_embedding import BaseEmbedding
from services.embeddings.ollama_embedding import OllamaEmbedding


class EmbeddingFactory:
    """
    Factory for embedding providers.
    """

    @staticmethod
    def create() -> BaseEmbedding:
        """
        Return the configured embedding provider.
        """

        return OllamaEmbedding()
