from schemas.health.knowledge_health import (
    KnowledgeHealth,
)
from schemas.review.review_status import (
    ReviewStatus,
)
from services.knowledge_review.review_repository import (
    ReviewRepository,
)


class KnowledgeHealthService:
    """
    Calculates overall knowledge base health.

    Current:
    - Rule-based aggregation

    Future:
    - Real evaluation metrics
    - Historical trends
    - Time-series analytics
    """

    def __init__(self):

        self.repository = ReviewRepository()

    def calculate(self) -> KnowledgeHealth:

        reviews = self.repository.get_all()

        total_reviews = len(reviews)

        pending_reviews = sum(
            review.status == ReviewStatus.PENDING
            for review in reviews
        )

        completed_reviews = sum(
            review.status == ReviewStatus.COMPLETED
            for review in reviews
        )

        rejected_reviews = sum(
            review.status == ReviewStatus.REJECTED
            for review in reviews
        )

        if total_reviews == 0:

            return KnowledgeHealth()

        return KnowledgeHealth(

            total_reviews=total_reviews,

            pending_reviews=pending_reviews,

            completed_reviews=completed_reviews,

            rejected_reviews=rejected_reviews,

            average_faithfulness=1.0,

            average_groundedness=1.0,

            average_answer_correctness=1.0,

            average_context_precision=1.0,

            average_context_recall=1.0,

            average_citation_accuracy=1.0,

            average_retrieval_score=1.0,

            duplicate_rate=0.0,

            outdated_rate=0.0,

            overall_health_score=1.0,
        )
