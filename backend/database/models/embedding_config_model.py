"""
SQLAlchemy model for persisting dynamic embedding model registrations.

API keys are NEVER stored here — only registry metadata.
"""

from sqlalchemy import Column, String, Integer, Boolean, Text
from database.base import Base


class EmbeddingConfigModel(Base):
    __tablename__ = "embedding_configs"

    model_id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    billing = Column(String, nullable=False, default="unknown")
    requires_api_key = Column(Boolean, nullable=False, default=False)
    dimension = Column(Integer, nullable=False)
    description = Column(Text, nullable=True, default="")
    # Optional: underlying model_id when registry key differs (e.g. hf: prefix)
    underlying_model_id = Column(String, nullable=True)
