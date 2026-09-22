from datetime import datetime
from utils.datetime_utils import ist_now
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """
    Enterprise evaluation result for a single AI interaction.
    """

    evaluation_id: str = Field(default="")

    review_id: str = Field(default="")

    faithfulness: float = 0.0

    groundedness: float = 0.0

    answer_relevance: float = 0.0

    answer_correctness: float = 0.0

    context_precision: float = 0.0

    context_recall: float = 0.0

    citation_accuracy: float = 0.0

    hallucination_score: float = 0.0

    semantic_similarity: float = 0.0

    retrieval_score: float = 0.0

    overall_score: float = 0.0

    evaluated_by: str = Field(default="system")

    created_at: datetime = Field(
        default_factory=ist_now
    )
