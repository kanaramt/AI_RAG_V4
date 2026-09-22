from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from backend.database.base import Base
from backend.utils.datetime_utils import ist_now


class ConversationModel(Base):

    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    conversation_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    model = Column(
        String,
        nullable=True,
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