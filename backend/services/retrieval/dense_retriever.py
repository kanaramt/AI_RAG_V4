import os
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
    - Convert query into embeddings using the configured model
    - Perform dense vector search
    - Return standardized RetrievalResponse

    Accepts optional model_name and api_key so retrieval always uses
    the same embedding model that was used during ingestion.
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
    ):
        # Use explicitly provided model, fall back to active model from env
        resolved_model = (
            model_name
            or os.getenv("ACTIVE_EMBEDDING_MODEL")
        )

        self.embedding_service = EmbeddingService(
            model_name=resolved_model,
            api_key=api_key,
        )

        self.vector_store = VectorStoreFactory.create()

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        start_time = time.perf_counter()

        requested_model = (
            request.embedding_model
            or self.embedding_service.model
        )

        requested_api_key = request.embedding_api_key

        if (
            requested_model != self.embedding_service.model
            or requested_api_key
        ):
            embedding_service = EmbeddingService(
                model_name=requested_model,
                api_key=requested_api_key,
            )
        else:
            embedding_service = self.embedding_service

        query_embedding = embedding_service.generate_embedding(
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
