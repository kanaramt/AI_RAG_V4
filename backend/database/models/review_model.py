from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from utils.datetime_utils import ist_now
from database.base import Base


class ReviewModel(Base):
    """
    SQLAlchemy model for Knowledge Reviews.
    """

    __tablename__ = "knowledge_reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    review_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    conversation_id: Mapped[str] = mapped_column(
        String(64),
        default="",
    )

    username: Mapped[str] = mapped_column(
        String(100),
        default="",
    )

    original_prompt: Mapped[str] = mapped_column(
        String,
    )

    rewritten_query: Mapped[str] = mapped_column(
        String,
        default="",
    )

    llm_response: Mapped[str] = mapped_column(
        String,
    )

    retrieval_strategy: Mapped[str] = mapped_column(
        String(50),
        default="",
    )

    llm_model: Mapped[str] = mapped_column(
        String(100),
        default="",
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=ist_now,
    )
