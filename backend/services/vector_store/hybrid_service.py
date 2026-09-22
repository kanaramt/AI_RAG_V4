from services.vector_store.base import BaseVectorStore
from services.vector_store.qdrant_service import QdrantService
from services.vector_store.faiss_service import FaissService


class HybridVectorStore(BaseVectorStore):
    """
    Enterprise Hybrid Vector Store.

    Writes to:
    - Qdrant (Persistent)
    - FAISS (Fast in-memory)

    Reads will later combine both.
    """

    def __init__(self):

        self.qdrant = QdrantService()
        self.faiss = FaissService()

        print("[OK] Hybrid Vector Store initialized.")

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
    ):

        self.qdrant.add_documents(
            ids,
            documents,
            embeddings,
            metadatas,
        )

        self.faiss.add_documents(
            ids,
            documents,
            embeddings,
            metadatas,
        )

    def search_dense(
        self,
        query_embedding,
        top_k=10,
        filters=None,
    ):
        """
        Hybrid dense search.

        Will combine FAISS + Qdrant.
        """

        return self.qdrant.search_dense(
        query_embedding=query_embedding,
        top_k=top_k,
        filters=filters,
    )

    def delete_documents(
        self,
        ids,
    ):
        """
        Will delete from both stores later.
        """
        pass

    def health_check(self):

        return {
            "qdrant": self.qdrant.health_check(),
            "faiss": self.faiss.health_check(),
        }


if __name__ == "__main__":
    HybridVectorStore()
