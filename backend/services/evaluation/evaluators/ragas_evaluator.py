from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)

from .base_evaluator import BaseEvaluator


class RagasEvaluator(BaseEvaluator):
    """
    Adapter for the RAGAS evaluation framework.

    Current:
    Placeholder adapter.

    Future:
    This class will execute real RAGAS metrics.
    """

    def evaluate(
        self,
        review: KnowledgeReview,
    ) -> EvaluationResult:

        raise NotImplementedError(
            "RAGAS integration will be implemented "
            "in the production phase."
        )
