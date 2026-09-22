from datetime import datetime
from utils.datetime_utils import ist_now
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
)

from database.base import Base


class IngestionHistoryModel(Base):

    __tablename__ = "ingestion_history"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id = Column(
        String,
        nullable=False,
    )

    asset_id = Column(
        String,
        nullable=True,
    )

    action = Column(
        String,
        nullable=False,
    )

    source_type = Column(
        String,
        nullable=True,
    )

    source_name = Column(
        String,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
    )

    details_json = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )
