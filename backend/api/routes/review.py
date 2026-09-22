from fastapi import APIRouter

from schemas.review.knowledge_review import (
    KnowledgeReview,
)
from schemas.review.review_status import (
    ReviewStatus,
)
from services.knowledge_review.review_service import (
    ReviewService,
)
from services.recommendation.recommendation_service import (
    RecommendationService,
)

router = APIRouter(
    prefix="/reviews",
    tags=["Knowledge Review"],
)

review_service = ReviewService()

recommendation_service = (
    RecommendationService()
)


@router.post("/")
async def create_review(
    review: KnowledgeReview,
):
    (
        review,
        evaluation,
        recommendation,
    ) = review_service.create_review(
        review
    )

    return {
        "review": review,
        "evaluation": evaluation,
        "recommendation": recommendation,
    }

    return {
        "review": review,
        "evaluation": evaluation,
    }


@router.get("/")
async def get_reviews():
    return review_service.get_reviews()


@router.get("/pending")
async def get_pending_reviews():
    return review_service.get_pending_reviews()


@router.get("/analytics")
async def get_review_analytics():

    return review_service.get_analytics()

@router.put("/{review_id}/{status}")
async def update_review_status(
    review_id: str,
    status: ReviewStatus,
):
    return {
        "success": review_service.update_status(
            review_id,
            status,
        )
    }

@router.get(
    "/recommendations/analytics"
)
async def get_recommendation_analytics():

    return (
        recommendation_service.get_analytics()
    )
