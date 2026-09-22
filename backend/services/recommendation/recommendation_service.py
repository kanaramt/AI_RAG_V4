import uuid

from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from schemas.recommendation.recommendation_result import (
    RecommendationResult,
)

from database.session import SessionLocal

from services.recommendation.recommendation_sql_repository import (
    RecommendationSQLRepository,
)

from services.recommendation.recommendation_analytics import (
    RecommendationAnalytics,
)

class RecommendationService:
    """
    Enterprise Recommendation Engine.

    Current:
    Rule-based recommendations.

    Future:
    AI-driven recommendations using
    evaluation history, feedback,
    retrieval quality and trends.
    """

    def __init__(self):

        self.analytics = (
            RecommendationAnalytics()   
        )

    def recommend(
        self,
        evaluation: EvaluationResult,
    ) -> RecommendationResult:

        recommendation = RecommendationResult(
            recommendation_id=str(uuid.uuid4()),
            review_id=evaluation.review_id,
            recommendation_type="none",
            confidence=1.0,
            reason="Knowledge quality is acceptable.",
        )

        if evaluation.faithfulness < 0.70:

            recommendation.recommendation_type = (
                "manual_review"
            )
            recommendation.reason = (
                "Low faithfulness detected."
            )
            recommendation.confidence = 0.95

        elif evaluation.citation_accuracy < 0.80:

            recommendation.recommendation_type = (
                "update_chunk"
            )
            recommendation.reason = (
                "Citation accuracy is low."
            )
            recommendation.confidence = 0.90

        elif evaluation.context_precision < 0.75:

            recommendation.recommendation_type = (
                "reembed"
            )
            recommendation.reason = (
                "Poor context precision."
            )
            recommendation.confidence = 0.88

        elif evaluation.hallucination_score > 0.30:

            recommendation.recommendation_type = (
                "manual_review"
            )
            recommendation.reason = (
                "Possible hallucination detected."
            )
            recommendation.confidence = 0.99

        db = SessionLocal()

        try:

            repository = (
                RecommendationSQLRepository(db)
            )

            repository.create(
                recommendation
            )

        finally:

            db.close()

        return recommendation

    def get_analytics(
        self,
    ) -> dict:

        db = SessionLocal()

        try:

            repository = (
                RecommendationSQLRepository(db)
            )

            recommendations = (
                repository.get_all()
            )

            return self.analytics.summary(
                recommendations
            )

        finally:

            db.close()
