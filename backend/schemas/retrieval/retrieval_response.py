from pydantic import BaseModel, Field

from schemas.retrieval.retrieval_metrics import RetrievalMetrics
from schemas.retrieval.retrieved_document import RetrievedDocument
from schemas.retrieval.source_reference import SourceReference


class RetrievalResponse(BaseModel):
    """
    Standard response returned by every retriever.
    """

    documents: list[RetrievedDocument] = Field(
        default_factory=list,
        description="Retrieved documents."
    )

    total_documents: int = Field(
        default=0,
        description="Number of retrieved documents."
    )

    retrieval_time_ms: float = Field(
        default=0.0,
        description="Time taken for retrieval."
    )

    retriever_name: str = Field(
        default="",
        description="Retriever that generated this response."
    )

    metrics: RetrievalMetrics = Field(
        default_factory=RetrievalMetrics,
        description="Detailed retrieval pipeline metrics."
    )

    sources: list[SourceReference] = Field(
        default_factory=list,
        description="Sources used to generate the answer."
    )
