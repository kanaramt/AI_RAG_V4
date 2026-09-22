from abc import ABC, abstractmethod


class BaseChunker(ABC):
    """
    Base interface for all chunking strategies.
    """

    @abstractmethod
    def chunk(
        self,
        text: str,
    ) -> list[str]:
        """
        Split text into chunks.
        """
        pass
