from datetime import datetime
from utils.datetime_utils import ist_now
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    JSON,
)

from database.base import Base


class KnowledgeAssetModel(Base):
    """
    SQLAlchemy model for persistent Knowledge Assets.
    """

    __tablename__ = "knowledge_assets"

    asset_id = Column(
        String,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    source_type = Column(
        String,
        nullable=False,
    )

    source_name = Column(
        String,
        nullable=False,
    )

    source_path = Column(
        String,
        nullable=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    owner = Column(
        String,
        default="",
    )

    department = Column(
        String,
        default="",
    )

    tags = Column(
        Text,
        default="",
    )

    language = Column(
        String,
        default="en",
    )

    chunk_count = Column(
        Integer,
        default=0,
    )

    embedding_model = Column(
        String,
        default="",
    )

    vector_store = Column(
        String,
        default="",
    )

    status = Column(
        String,
        nullable=False,
    )

    version = Column(
        Integer,
        default=1,
    )

    health_score = Column(
        Float,
        default=0.0,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=ist_now,
        onupdate=ist_now,
    )

    metadata_json = Column(
        JSON,
        nullable=True,
    )
