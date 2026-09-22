from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from backend.database.base import Base
from backend.utils.datetime_utils import ist_now


class MessageModel(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    message_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    conversation_id = Column(
        String,
        ForeignKey("conversations.conversation_id"),
        nullable=False,
        index=True,
    )

    sender = Column(
        String,
        nullable=False,
    )

    text = Column(
        Text,
        nullable=False,
    )

    attachments = Column(
        JSONB,
        nullable=True,
    )

    citations = Column(
        JSONB,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )