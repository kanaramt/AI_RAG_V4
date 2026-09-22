from services.vector_store.base import BaseVectorStore


class FaissService(BaseVectorStore):
    """
    Enterprise FAISS implementation.

    Used as a fast in-memory vector index.
    """

    VECTOR_SIZE = 768

    def __init__(self):
        self._index = None
        self.documents = []
        self.metadatas = []

    @property
    def index(self):
        if self._index is None:
            import faiss
            self._index = faiss.IndexFlatIP(self.VECTOR_SIZE)
            print("[OK] FAISS index initialized.")
        return self._index

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
    ):
        """
        Store vectors inside FAISS.
        """
        import numpy as np
        import faiss

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.documents.extend(documents)
        self.metadatas.extend(metadatas)

        print(f"[OK] Stored {len(documents)} vectors in FAISS.")

    def search_dense(
        self,
        query_embedding,
        top_k=10,
        filters=None,
    ):
        """
        Dense semantic search using FAISS.
        """
        import numpy as np
        import faiss

        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, top_k)

        class MockPoint:
            def __init__(self, point_id, score, payload):
                self.id = point_id
                self.score = score
                self.payload = payload

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.documents):
                continue
                
            metadata = self.metadatas[idx] or {}
            
            # Simple metadata filtering
            if filters:
                match = True
                for k, v in filters.items():
                    if metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            results.append(
                MockPoint(
                    point_id=str(idx),
                    score=float(dist),
                    payload={
                        "text": self.documents[idx],
                        **metadata
                    }
                )
            )
        return results

    def delete_documents(
        self,
        ids,
    ):
        """
        Placeholder. Rebuilding not strictly required for local mock.
        """
        print(f"FAISS delete documents called for: {ids}")

    def health_check(self):
        """
        Return the count of stored vectors.
        """
        return {
            "status": "healthy",
            "vectors_count": self.index.ntotal
        }


if __name__ == "__main__":
    FaissService()
