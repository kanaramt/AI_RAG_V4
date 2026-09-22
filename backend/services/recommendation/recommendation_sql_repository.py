from sqlalchemy.orm import Session

from database.models.recommendation_model import (
    RecommendationModel,
)
from schemas.recommendation.recommendation_result import (
    RecommendationResult,
)


class RecommendationSQLRepository:
    """
    SQL repository for Recommendations.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        recommendation: RecommendationResult,
    ) -> RecommendationResult:

        model = RecommendationModel(
            recommendation_id=recommendation.recommendation_id,
            review_id=recommendation.review_id,
            recommendation_type=recommendation.recommendation_type,
            confidence=recommendation.confidence,
            reason=recommendation.reason,
            created_at=recommendation.created_at,
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)

        return recommendation

    def get_all(
        self,
    ) -> list[RecommendationResult]:

        models = self.db.query(
            RecommendationModel
        ).all()

        return [
            self._to_schema(model)
            for model in models
        ]
    def get_all(
        self,
    ) -> list[RecommendationResult]:

        models = self.db.query(
            RecommendationModel
        ).all()

        return [
            self._to_schema(model)
            for model in models
        ]
    def _to_schema(
        self,
        model: RecommendationModel,
    ) -> RecommendationResult:

        return RecommendationResult(
            recommendation_id=model.recommendation_id,
            review_id=model.review_id,
            recommendation_type=model.recommendation_type,
            confidence=model.confidence,
            reason=model.reason,
            created_at=model.created_at,
        )
