from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)

from .base_evaluator import BaseEvaluator
from .rule_evaluator import RuleEvaluator


class CompositeEvaluator(BaseEvaluator):
    """
    Enterprise Evaluation Orchestrator.

    Future pipeline

    Rule Evaluator
          +
    RAGAS
          +
    DeepEval
          +
    Phoenix
          +
    LangSmith
    """

    def __init__(self):

        self.rule_evaluator = RuleEvaluator()

    def evaluate(
        self,
        review: KnowledgeReview,
    ) -> EvaluationResult:

        result = self.rule_evaluator.evaluate(
            review
        )

        result.evaluated_by = (
            "CompositeEvaluator"
        )

        return result
