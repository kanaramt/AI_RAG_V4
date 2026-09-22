import threading
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from services.vector_store.base import BaseVectorStore
from settings import settings

_qdrant_lock = threading.Lock()
_shared_qdrant_client = None
_initialized_collections = set()


def get_shared_qdrant_client() -> QdrantClient:
    global _shared_qdrant_client
    if _shared_qdrant_client is None:
        with _qdrant_lock:
            if _shared_qdrant_client is None:
                import os
                qdrant_url = os.getenv("QDRANT_URL") or getattr(settings, "QDRANT_URL", None)
                qdrant_api_key = os.getenv("QDRANT_API_KEY") or getattr(settings, "QDRANT_API_KEY", None)

                if qdrant_url:
                    print(f"[QdrantService] Connecting to Qdrant server at {qdrant_url}...")
                    _shared_qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key or None, timeout=60.0)
                else:
                    db_path = str(settings.BACKEND_DIR / "qdrant_db")
                    print(f"[QdrantService] Using local filesystem storage at {db_path}...")
                    _shared_qdrant_client = QdrantClient(path=db_path)
    return _shared_qdrant_client


class QdrantService(BaseVectorStore):
    """
    Enterprise implementation of the Vector Store using Qdrant.
    """

    COLLECTION_NAME = "knowledge_base"
    VECTOR_SIZE = 768

    def __init__(self, collection_name: str = None):
        self.collection_name = collection_name or self.COLLECTION_NAME

    @property
    def client(self) -> QdrantClient:
        client = get_shared_qdrant_client()
        if self.collection_name not in _initialized_collections:
            with _qdrant_lock:
                if self.collection_name not in _initialized_collections:
                    try:
                        client.get_collection(self.collection_name)
                        print(f"[OK] Qdrant collection '{self.collection_name}' is ready.")
                    except Exception:
                        client.recreate_collection(
                            collection_name=self.collection_name,
                            vectors_config=VectorParams(
                                size=self.VECTOR_SIZE,
                                distance=Distance.COSINE,
                            ),
                        )
                        print(f"[OK] Created Qdrant collection '{self.collection_name}'.")
                    _initialized_collections.add(self.collection_name)
        return client

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
        batch_size: int = 100,
    ):
        points = []

        for idx in range(len(documents)):
            points.append(
                PointStruct(
                    id=ids[idx],
                    vector=embeddings[idx],
                    payload={
                        "text": documents[idx],
                        **metadatas[idx],
                    },
                )
            )

        # Batch upsert points to Qdrant to prevent gRPC payload size limitations and memory overflows
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        print(f"[OK] Stored {len(points)} vectors in Qdrant collection '{self.collection_name}' (batched by {batch_size}).")

    def search_dense(
        self,
        query_embedding,
        top_k=10,
        filters=None,
    ):
        """
        Perform dense semantic search using Qdrant.
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        qdrant_filter = None
        if filters:
            conditions = []
            for key, val in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=val)
                    )
                )
            qdrant_filter = Filter(must=conditions)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            query_filter=qdrant_filter,
        )

        return results.points

    def delete_documents(
        self,
        ids,
    ):
        """
        Delete documents by ID from Qdrant.
        """
        from qdrant_client.models import PointIdsList
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=ids)
        )
        print(f"[OK] Deleted points {ids} from Qdrant collection '{self.collection_name}'.")

    def health_check(self):
        """
        Check if collection is readable.
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "status": "healthy",
                "collection": self.collection_name,
                "vectors_count": info.points_count
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


if __name__ == "__main__":
    from settings import settings
    QdrantService()
