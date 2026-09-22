from datetime import datetime
from typing import Literal
from utils.datetime_utils import ist_now
from pydantic import BaseModel, Field


class RecommendationResult(BaseModel):
    """
    AI-generated recommendation for a Knowledge Review.
    """

    recommendation_id: str = Field(default="")

    review_id: str = Field(default="")

    recommendation_type: Literal[
        "update_chunk",
        "delete_chunk",
        "merge_chunks",
        "reembed",
        "update_metadata",
        "archive_document",
        "manual_review",
        "none",
    ] = "none"

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    reason: str = Field(default="")

    created_at: datetime = Field(
        default_factory=ist_now
    )
