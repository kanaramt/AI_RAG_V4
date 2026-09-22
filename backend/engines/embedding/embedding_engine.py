"""
Enterprise Embedding Engine

Orchestrates embedding generation.
"""

from typing import List

from services.embedding_service import EmbeddingService


class EmbeddingEngine:
    """
    Orchestrates embedding generation.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        return self.embedding_service.generate_embedding(text)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """
        return self.embedding_service.generate_embeddings(texts)
