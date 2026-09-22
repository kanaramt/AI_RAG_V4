from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)
from schemas.review.review_status import (
    ReviewStatus,
)


class ReviewAnalytics:
    """
    Enterprise Review Analytics.
    """

    def summary(
        self,
        reviews: list[KnowledgeReview],
        evaluations: list[EvaluationResult],
    ) -> dict:

        total_reviews = len(reviews)

        pending_reviews = sum(
            1
            for review in reviews
            if review.status == ReviewStatus.PENDING
        )

        approved_reviews = sum(
            1
            for review in reviews
            if review.status == ReviewStatus.APPROVED
        )

        rejected_reviews = sum(
            1
            for review in reviews
            if review.status == ReviewStatus.REJECTED
        )

        average_score = (
            sum(
                evaluation.overall_score
                for evaluation in evaluations
            )
            / len(evaluations)
            if evaluations
            else 0.0
        )

        average_faithfulness = (
            sum(
                evaluation.faithfulness
                for evaluation in evaluations
            )
            / len(evaluations)
            if evaluations
            else 0.0
        )

        average_groundedness = (
            sum(
                evaluation.groundedness
                for evaluation in evaluations
            )
            / len(evaluations)
            if evaluations
            else 0.0
        )

        average_relevance = (
            sum(
                evaluation.answer_relevance
                for evaluation in evaluations
            )
            / len(evaluations)
            if evaluations
            else 0.0
        )

        return {
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "approved_reviews": approved_reviews,
            "rejected_reviews": rejected_reviews,
            "average_score": round(
                average_score,
                2,
            ),
            "average_faithfulness": round(
                average_faithfulness,
                2,
            ),
            "average_groundedness": round(
                average_groundedness,
                2,
            ),
            "average_relevance": round(
                average_relevance,
                2,
            ),
        }
