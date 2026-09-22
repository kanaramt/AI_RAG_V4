from schemas.review.knowledge_review import (
    KnowledgeReview,
)
from schemas.review.review_status import (
    ReviewStatus,
)


class ReviewRepository:
    """
    Temporary in-memory repository.

    Future:
    PostgreSQL
    MongoDB
    Elasticsearch
    """

    def __init__(self):

        self._reviews: list[KnowledgeReview] = []

    def create(
        self,
        review: KnowledgeReview,
    ) -> KnowledgeReview:

        self._reviews.append(review)

        return review

    def get_all(
        self,
    ) -> list[KnowledgeReview]:

        return self._reviews

    def get_pending(
        self,
    ) -> list[KnowledgeReview]:

        return [
            review
            for review in self._reviews
            if review.status == ReviewStatus.PENDING
        ]

    def update_status(
        self,
        review_id: str,
        status: ReviewStatus,
    ) -> bool:

        for review in self._reviews:

            if review.review_id == review_id:

                review.status = status

                return True

        return False
