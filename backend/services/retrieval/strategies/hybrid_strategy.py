import time

from schemas.retrieval.retrieval_metrics import RetrievalMetrics
from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse

from services.retrieval.context_builder import ContextBuilder
from services.retrieval.dense_retriever import DenseRetriever
from services.retrieval.metadata_filter import MetadataFilter
from services.retrieval.query_rewriter import QueryRewriter
from services.retrieval.reranker import Reranker
from services.retrieval.score_fusion import ScoreFusion
from services.retrieval.source_grounding import (
    SourceGroundingService,
)
from services.retrieval.sparse_retriever import SparseRetriever

from .base_strategy import BaseRetrievalStrategy


class HybridStrategy(BaseRetrievalStrategy):
    """
    Enterprise Hybrid Retrieval Strategy.
    """

    def __init__(self):

        self.query_rewriter = QueryRewriter()

        self.dense = DenseRetriever()

        self.sparse = SparseRetriever()

        self.fusion = ScoreFusion()

        self.metadata_filter = MetadataFilter()

        self.reranker = Reranker()

        self.context_builder = ContextBuilder()

        self.source_grounding = SourceGroundingService()

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResponse, str]:

        print("[HYBRID STRATEGY] START")

        metrics = RetrievalMetrics()

        pipeline_start = time.perf_counter()

        # -------------------------------
        # Query Rewrite
        # -------------------------------

        start = time.perf_counter()

        rewritten_query = await self.query_rewriter.rewrite(
            request.query
        )

        metrics.query_rewrite_ms = (
            time.perf_counter() - start
        ) * 1000

        retrieval_request = request.model_copy(
            update={"query": rewritten_query}
        )

        # -------------------------------
        # Dense Retrieval
        # -------------------------------

        start = time.perf_counter()

        dense_response = self.dense.retrieve(
            retrieval_request
        )

        metrics.dense_retrieval_ms = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"[DEBUG] Dense Retrieval -> "
            f"{len(dense_response.documents)} docs"
        )

        # -------------------------------
        # Sparse Retrieval
        # -------------------------------

        start = time.perf_counter()

        sparse_response = self.sparse.retrieve(
            retrieval_request
        )

        metrics.sparse_retrieval_ms = (
            time.perf_counter() - start
        ) * 1000
        print(
            f"[DEBUG] Sparse Retrieval -> "
            f"{len(sparse_response.documents)} docs"
        )
        # -------------------------------
        # Fusion
        # -------------------------------

        start = time.perf_counter()

        fused_documents = self.fusion.fuse(
            dense_response.documents,
            sparse_response.documents,
        )

        metrics.fusion_ms = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"[DEBUG] Fusion -> "
            f"{len(fused_documents)} docs"
        )

        # -------------------------------
        # Metadata Filter
        # -------------------------------

        start = time.perf_counter()

        filtered_documents = self.metadata_filter.filter(
            fused_documents,
            request.filters,
        )

        metrics.metadata_filter_ms = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"[DEBUG] Metadata Filter -> "
            f"{len(filtered_documents)} docs"
        )

        # -------------------------------
        # Reranker
        # -------------------------------

        start = time.perf_counter()

        reranked_documents = self.reranker.rerank(
            request.query,
            filtered_documents,
            # top_k passed from request; strictly caps chunks sent to LLM (token cost control)
            top_k=request.top_k,
        )

        print(
            f"[DEBUG] Reranker -> "
            f"{len(reranked_documents)} docs"
        )

        for doc in reranked_documents:
            print(
                f"[DEBUG] Score={doc.score:.4f}"
            )

        metrics.reranking_ms = (
            time.perf_counter() - start
        ) * 1000

        # -------------------------------
        # Context Builder
        # -------------------------------

        start = time.perf_counter()

        context = await self.context_builder.build(
            query=request.query,
            documents=reranked_documents,
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        metrics.context_build_ms = elapsed
        metrics.context_compression_ms = elapsed

        # -------------------------------
        # Source Grounding
        # -------------------------------

        sources = self.source_grounding.build(
            reranked_documents
        )

        # -------------------------------
        # Total
        # -------------------------------

        metrics.total_retrieval_ms = (
            time.perf_counter() - pipeline_start
        ) * 1000

        response = RetrievalResponse(
            documents=reranked_documents,
            total_documents=len(reranked_documents),
            retrieval_time_ms=metrics.total_retrieval_ms,
            retriever_name="HybridStrategy",
            metrics=metrics,
            sources=sources,
        )

        print(
            f"[DEBUG] Final Context Length = "
            f"{len(context)}"
        )

        return response, context
