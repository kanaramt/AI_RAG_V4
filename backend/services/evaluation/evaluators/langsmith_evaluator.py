from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)

from .base_evaluator import BaseEvaluator


class LangSmithEvaluator(BaseEvaluator):
    """
    Adapter for LangSmith evaluation.

    Current:
    Placeholder adapter.

    Future:
    Executes LangSmith datasets,
    traces and evaluation pipelines.
    """

    def evaluate(
        self,
        review: KnowledgeReview,
    ) -> EvaluationResult:

        raise NotImplementedError(
            "LangSmith integration will be implemented "
            "in the production phase."
        )
