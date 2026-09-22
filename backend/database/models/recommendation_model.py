from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from backend.utils.datetime_utils import ist_now
from backend.database.base import Base


class RecommendationModel(Base):
    """
    SQLAlchemy model for Recommendations.
    """

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    recommendation_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    review_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    recommendation_type: Mapped[str] = mapped_column(
        String(100),
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    reason: Mapped[str] = mapped_column(
        String,
        default="",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=ist_now,
    )