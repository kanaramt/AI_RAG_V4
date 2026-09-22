from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import String
from utils.datetime_utils import ist_now
from database.base import Base


class KnowledgeReviewModel(Base):
    __tablename__ = "knowledge_reviews"

    review_id = Column(
        String,
        primary_key=True,
    )

    document_id = Column(
        String,
        nullable=False,
    )

    reviewer = Column(
        String,
        nullable=False,
    )

    score = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )
