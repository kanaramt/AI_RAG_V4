from pydantic import BaseModel, Field


class RetrievalMetrics(BaseModel):
    """
    Performance metrics for the retrieval pipeline.
    """

    query_rewrite_ms: float = Field(default=0.0)

    dense_retrieval_ms: float = Field(default=0.0)

    sparse_retrieval_ms: float = Field(default=0.0)

    fusion_ms: float = Field(default=0.0)

    metadata_filter_ms: float = Field(default=0.0)

    reranking_ms: float = Field(default=0.0)

    context_build_ms: float = Field(default=0.0)

    context_compression_ms: float = Field(default=0.0)

    total_retrieval_ms: float = Field(default=0.0)
