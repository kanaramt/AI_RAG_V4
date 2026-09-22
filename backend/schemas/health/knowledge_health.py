from datetime import datetime

from pydantic import BaseModel, Field
from utils.datetime_utils import ist_now

class KnowledgeHealth(BaseModel):
    """
    Overall health of the enterprise knowledge base.
    """

    total_reviews: int = 0

    pending_reviews: int = 0

    completed_reviews: int = 0

    rejected_reviews: int = 0

    average_faithfulness: float = 0.0

    average_groundedness: float = 0.0

    average_answer_correctness: float = 0.0

    average_context_precision: float = 0.0

    average_context_recall: float = 0.0

    average_citation_accuracy: float = 0.0

    average_retrieval_score: float = 0.0

    duplicate_rate: float = 0.0

    outdated_rate: float = 0.0

    overall_health_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    calculated_at: datetime = Field(
        default_factory=ist_now
    )
