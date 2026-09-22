from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from backend.utils.datetime_utils import ist_now
from backend.database.base import Base


class EvaluationModel(Base):
    """
    SQLAlchemy model for Evaluation Results.
    """

    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    evaluation_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    review_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    faithfulness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    groundedness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    answer_relevance: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    answer_correctness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    context_precision: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    context_recall: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    citation_accuracy: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    hallucination_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    semantic_similarity: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    retrieval_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    evaluated_by: Mapped[str] = mapped_column(
        String(100),
        default="",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=ist_now,
    )