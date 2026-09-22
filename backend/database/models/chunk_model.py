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


class ChunkModel(Base):

    __tablename__ = "chunks"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    chunk_id = Column(
        String,
        unique=True,
        nullable=False,
    )

    document_id = Column(
        String,
        nullable=False,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    metadata_json = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )
