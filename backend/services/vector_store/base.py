from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    """
    Base interface for every vector database.
    """

    @abstractmethod
    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
    ):
        """
        Store vectors in the database.
        """
        pass

    @abstractmethod
    def search_dense(
        self,
        query_embedding,
        top_k=10,
        filters=None,
    ):
        """
        Dense semantic search.
        """
        pass

    @abstractmethod
    def delete_documents(
        self,
        ids,
    ):
        """
        Delete vectors from the database.
        """
        pass

    @abstractmethod
    def health_check(self):
        """
        Check whether the vector database is available.
        """
        pass
