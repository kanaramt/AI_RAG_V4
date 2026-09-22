from datetime import datetime
from backend.schemas.review.review_status import ReviewStatus

from pydantic import BaseModel, Field

from backend.schemas.feedback.knowledge_feedback import (
    KnowledgeFeedback,
)
from backend.schemas.retrieval.retrieval_metrics import (
    RetrievalMetrics,
)
from backend.schemas.retrieval.source_reference import (
    SourceReference,
)
from backend.utils.datetime_utils import ist_now

class KnowledgeReview(BaseModel):
    """
    Enterprise Knowledge Review Record.
    """

    review_id: str = Field(default="")

    conversation_id: str = Field(default="")

    username: str = Field(default="")

    original_prompt: str = Field(default="")

    rewritten_query: str = Field(default="")

    llm_response: str = Field(default="")

    retrieval_strategy: str = Field(default="")

    llm_model: str = Field(default="")

    metrics: RetrievalMetrics = Field(
        default_factory=RetrievalMetrics
    )

    sources: list[SourceReference] = Field(
        default_factory=list
    )

    feedback: list[KnowledgeFeedback] = Field(
        default_factory=list
    )

    status: ReviewStatus = ReviewStatus.PENDING

    created_at: datetime = Field(
        default_factory=ist_now
    )

    updated_at: datetime = Field(
        default_factory=ist_now
    )