from datetime import datetime
from utils.datetime_utils import ist_now
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)

from database.base import Base


class DocumentModel(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id = Column(
        String,
        unique=True,
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    source_type = Column(
        String,
        nullable=False,
    )

    source_name = Column(
        String,
        nullable=False,
    )

    metadata_json = Column(
        JSON,
        nullable=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )
