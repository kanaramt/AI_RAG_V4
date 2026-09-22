from sqlalchemy.orm import Session

from database.models.evaluation_model import (
    EvaluationModel,
)
from schemas.evaluation.evaluation_result import (
    EvaluationResult,
)


class EvaluationSQLRepository:
    """
    SQL repository for Evaluation Results.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        evaluation: EvaluationResult,
    ) -> EvaluationResult:

        model = EvaluationModel(
            evaluation_id=evaluation.evaluation_id,
            review_id=evaluation.review_id,
            faithfulness=evaluation.faithfulness,
            groundedness=evaluation.groundedness,
            answer_relevance=evaluation.answer_relevance,
            answer_correctness=evaluation.answer_correctness,
            context_precision=evaluation.context_precision,
            context_recall=evaluation.context_recall,
            citation_accuracy=evaluation.citation_accuracy,
            hallucination_score=evaluation.hallucination_score,
            semantic_similarity=evaluation.semantic_similarity,
            retrieval_score=evaluation.retrieval_score,
            overall_score=evaluation.overall_score,
            evaluated_by=evaluation.evaluated_by,
            created_at=evaluation.created_at,
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)

        return evaluation

    def get_all(
        self,
    ) -> list[EvaluationResult]:

        models = self.db.query(
            EvaluationModel
        ).all()

        return [
            self._to_schema(model)
            for model in models
        ]

    def _to_schema(
        self,
        model: EvaluationModel,
    ) -> EvaluationResult:

        return EvaluationResult(
            evaluation_id=model.evaluation_id,
            review_id=model.review_id,
            faithfulness=model.faithfulness,
            groundedness=model.groundedness,
            answer_relevance=model.answer_relevance,
            answer_correctness=model.answer_correctness,
            context_precision=model.context_precision,
            context_recall=model.context_recall,
            citation_accuracy=model.citation_accuracy,
            hallucination_score=model.hallucination_score,
            semantic_similarity=model.semantic_similarity,
            retrieval_score=model.retrieval_score,
            overall_score=model.overall_score,
            evaluated_by=model.evaluated_by,
            created_at=model.created_at,
        )
