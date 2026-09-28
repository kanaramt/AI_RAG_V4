from datetime import datetime

from sqlalchemy import Column, DateTime, String

from database.base import Base


class ActiveEmbeddingSettingModel(Base):
    """
    Persists the currently selected embedding model.

    This stores only the model selection/metadata reference.
    API keys are never stored here.
    """

    __tablename__ = "active_embedding_settings"

    setting_key = Column(
        String,
        primary_key=True,
        nullable=False,
        default="default",
    )

    model_id = Column(
        String,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
