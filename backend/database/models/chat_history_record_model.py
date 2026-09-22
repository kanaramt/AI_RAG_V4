from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from backend.database.base import Base
from backend.utils.datetime_utils import ist_now


class ChatHistoryRecordModel(Base):

    __tablename__ = "chat_history_records"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    record_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    conversation_id = Column(
        String,
        nullable=False,
        index=True,
    )

    timestamp_ist = Column(
        DateTime(timezone=True),
        default=ist_now,
    )

    user_prompt = Column(
        Text,
        nullable=True,
    )

    retrieved_response = Column(
        Text,
        nullable=True,
    )

    correctness_score = Column(
        Float,
        default=0.0,
    )

    faithfulness_score = Column(
        Float,
        default=0.0,
    )

    groundedness_score = Column(
        Float,
        default=0.0,
    )

    confidence_score = Column(
        Float,
        default=0.0,
    )

    time_taken_seconds = Column(
        Float,
        default=0.0,
    )

    similarity_score = Column(
        Float,
        default=0.0,
    )

    llm_model = Column(
        String,
        nullable=True,
    )

    memory_source = Column(
        String,
        nullable=True,
    )

    files_used = Column(
        JSONB,
        nullable=True,
    )

    chunks_used = Column(
        JSONB,
        nullable=True,
    )

    chunk_metadata = Column(
        JSONB,
        nullable=True,
    )

    search_source = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )