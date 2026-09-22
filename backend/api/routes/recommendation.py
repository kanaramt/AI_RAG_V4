from fastapi import APIRouter

from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)
from services.recommendation.recommendation_service import (
    RecommendationService,
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendation"],
)

recommendation_service = RecommendationService()


@router.post("/")
async def generate_recommendation(
    evaluation: EvaluationResult,
):
    return recommendation_service.recommend(
        evaluation
    )
