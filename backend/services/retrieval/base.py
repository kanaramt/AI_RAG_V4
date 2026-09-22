from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    """
    Base interface for all retrieval strategies.
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: dict | None = None,
    ):
        """
        Retrieve the most relevant documents.
        """
        pass

    @abstractmethod
    def health_check(self):
        """
        Check whether the retriever is healthy.
        """
        pass
