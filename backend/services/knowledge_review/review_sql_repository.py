from sqlalchemy.orm import Session

from database.models.review_model import (
    ReviewModel,
)
from schemas.review.knowledge_review import (
    KnowledgeReview,
)
from schemas.review.review_status import (
    ReviewStatus,
)


class ReviewSQLRepository:
    """
    SQLAlchemy repository for Knowledge Reviews.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        review: KnowledgeReview,
    ) -> KnowledgeReview:

        model = ReviewModel(
            review_id=review.review_id,
            conversation_id=review.conversation_id,
            username=review.username,
            original_prompt=review.original_prompt,
            rewritten_query=review.rewritten_query,
            llm_response=review.llm_response,
            retrieval_strategy=review.retrieval_strategy,
            llm_model=review.llm_model,
            created_at=review.created_at,
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)

        return review

    def get_all(
        self,
    ) -> list[KnowledgeReview]:

        models = self.db.query(
            ReviewModel
        ).all()

        return [
            self._to_schema(model)
            for model in models
        ]
    def get_pending(
        self,
    ) -> list[KnowledgeReview]:

        models = (
            self.db.query(
                ReviewModel
            )
            .filter(
                ReviewModel.status
                == ReviewStatus.PENDING.value
            )
            .all()
        )

        return [
            self._to_schema(model)
            for model in models
        ] 

    def update_status(
        self,
        review_id: str,
        status: ReviewStatus,
    ) -> bool:

        return True
    
    def _to_schema(
        self,
        model: ReviewModel,
    ) -> KnowledgeReview:

        return KnowledgeReview(
        review_id=model.review_id,
        conversation_id=model.conversation_id,
        username=model.username,
        original_prompt=model.original_prompt,
        rewritten_query=model.rewritten_query,
        llm_response=model.llm_response,
        retrieval_strategy=model.retrieval_strategy,
        llm_model=model.llm_model,
        created_at=model.created_at,
    )
