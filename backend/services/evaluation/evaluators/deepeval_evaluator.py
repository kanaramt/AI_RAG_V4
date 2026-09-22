from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)

from .base_evaluator import BaseEvaluator


class DeepEvalEvaluator(BaseEvaluator):
    """
    Adapter for the DeepEval framework.

    Current:
    Placeholder adapter.

    Future:
    Executes real DeepEval metrics.
    """

    def evaluate(
        self,
        review: KnowledgeReview,
    ) -> EvaluationResult:

        raise NotImplementedError(
            "DeepEval integration will be implemented "
            "in the production phase."
        )
