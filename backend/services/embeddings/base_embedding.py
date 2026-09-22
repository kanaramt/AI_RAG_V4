from abc import ABC, abstractmethod


class BaseEmbedding(ABC):
    """
    Base interface for all embedding providers.
    """

    @abstractmethod
    def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """
        pass

    @abstractmethod
    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """
        pass
