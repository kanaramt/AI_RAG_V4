import time

from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse

from services.embedding_service import EmbeddingService
from services.retrieval.base import BaseRetriever
from services.vector_store.factory import VectorStoreFactory
from schemas.retrieval.retrieved_document import RetrievedDocument

class DenseRetriever(BaseRetriever):
    """
    Enterprise Dense Retriever.

    Responsibilities:
    - Convert query into embeddings
    - Perform dense vector search
    - Return standardized RetrievalResponse
    """

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.vector_store = VectorStoreFactory.create()

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        start_time = time.perf_counter()

        query_embedding = self.embedding_service.generate_embedding(
            request.query
        )

        results = self.vector_store.search_dense(
            query_embedding=query_embedding,
            top_k=request.top_k,
            filters=request.filters,
        )

        documents = []

        for point in results:

            payload = point.payload or {}

            documents.append(
                RetrievedDocument(
                    id=str(point.id),
                    text=payload.get("text", ""),
                    score=float(point.score),
                    source=payload.get("source", ""),
                    page=payload.get("page"),
                    metadata=payload,
                )
            )

        return RetrievalResponse(
            documents=documents,
            total_documents=len(documents),
            retrieval_time_ms=(
                time.perf_counter() - start_time
            ) * 1000,
            retriever_name="DenseRetriever",
    )

    def health_check(self):

        return {
            "status": "healthy",
            "vector_store": self.vector_store.health_check(),
        }
