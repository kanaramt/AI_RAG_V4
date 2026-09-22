from datetime import datetime
from typing import Literal
from backend.utils.datetime_utils import ist_now
from pydantic import BaseModel, Field


class KnowledgeFeedback(BaseModel):
    """
    User feedback associated with retrieved knowledge.
    """

    feedback_type: Literal[
        "answer",
        "citation",
        "document",
        "chunk",
    ]

    action: Literal[
        "positive",
        "negative",
        "update",
        "delete",
        "duplicate",
        "outdated",
    ]

    document_id: str = Field(default="")

    chunk_id: str = Field(default="")

    source: str = Field(default="")

    page: int | None = None

    comment: str = Field(
        default="",
        description="Optional user comment."
    )

    created_at: datetime = Field(
        default_factory=ist_now
    )