import uuid

from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)

from .base_evaluator import BaseEvaluator


class RuleEvaluator(BaseEvaluator):
    """
    Rule-based evaluator.

    This evaluator performs lightweight checks
    without requiring external LLMs.

    Future:
    - Retrieval quality
    - Source coverage
    - Response completeness
    - Context utilization
    """

    def evaluate(
        self,
        review: KnowledgeReview,
    ) -> EvaluationResult:

        source_count = len(review.sources)

        response_length = len(
            review.llm_response.strip()
        )

        faithfulness = 1.0 if source_count > 0 else 0.5

        groundedness = faithfulness

        answer_relevance = (
            1.0 if response_length > 30 else 0.6
        )

        answer_correctness = (
            faithfulness + answer_relevance
        ) / 2

        context_precision = (
            min(source_count / 5, 1.0)
            if source_count
            else 0.0
        )

        context_recall = context_precision

        citation_accuracy = (
            1.0 if source_count else 0.0
        )

        hallucination_score = (
            0.0 if source_count else 0.5
        )

        semantic_similarity = answer_relevance

        retrieval_score = (
            context_precision + citation_accuracy
        ) / 2

        overall_score = (
            faithfulness
            + groundedness
            + answer_relevance
            + answer_correctness
            + context_precision
            + context_recall
            + citation_accuracy
            + semantic_similarity
            + retrieval_score
        ) / 9

        return EvaluationResult(

            evaluation_id=str(uuid.uuid4()),

            review_id=review.review_id,

            faithfulness=faithfulness,

            groundedness=groundedness,

            answer_relevance=answer_relevance,

            answer_correctness=answer_correctness,

            context_precision=context_precision,

            context_recall=context_recall,

            citation_accuracy=citation_accuracy,

            hallucination_score=hallucination_score,

            semantic_similarity=semantic_similarity,

            retrieval_score=retrieval_score,

            overall_score=overall_score,

            evaluated_by="RuleEvaluator",
        )
