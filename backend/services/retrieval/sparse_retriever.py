import time

from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse
from schemas.retrieval.retrieved_document import RetrievedDocument

from services.retrieval.base import BaseRetriever


class SparseRetriever(BaseRetriever):
    """
    BM25 Keyword Retriever.
    """

    def __init__(self):

        self.documents = []

        self.tokenized_documents = []

        self.bm25 = None

    def build_index(
        self,
        documents: list[str],
    ):
        from rank_bm25 import BM25Okapi

        self.documents = documents

        self.tokenized_documents = [
            doc.lower().split()
            for doc in documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        start_time = time.perf_counter()

        if self.bm25 is None:

            return RetrievalResponse(
                documents=[],
                total_documents=0,
                retrieval_time_ms=(
                    time.perf_counter() - start_time
                ) * 1000,
                retriever_name="SparseRetriever",
            )

        query_tokens = request.query.lower().split()

        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True,
        )

        documents = []

        for index, score in ranked[: request.top_k]:

            documents.append(
                RetrievedDocument(
                    id=str(index),
                    text=self.documents[index],
                    score=float(score),
                )
            )

        return RetrievalResponse(
            documents=documents,
            total_documents=len(documents),
            retrieval_time_ms=(
                time.perf_counter() - start_time
            ) * 1000,
            retriever_name="SparseRetriever",
        )

    def health_check(self):

        return {
            "status": "healthy",
            "indexed_documents": len(self.documents),
        }
