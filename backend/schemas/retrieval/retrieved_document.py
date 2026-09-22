from typing import Any

from pydantic import BaseModel, Field


class RetrievedDocument(BaseModel):
    """
    Represents a single document returned by the retrieval engine.
    """

    id: str = Field(
        description="Unique document/chunk identifier."
    )

    text: str = Field(
        description="Retrieved chunk text."
    )

    score: float = Field(
        default=0.0,
        description="Retrieval relevance score."
    )

    source: str = Field(
        default="",
        description="Original source document."
    )

    page: int | None = Field(
        default=None,
        description="Page number if applicable."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata."
    )

    parent_id: str | None = Field(
        default=None,
        description="Parent document identifier."
    )

    chunk_id: str | None = Field(
        default=None,
        description="Child chunk identifier."
    )

    chunk_level: str = Field(
        default="child",
        description="Chunk level (parent or child)."
    )

    parent_text: str | None = Field(
        default=None,
        description="Parent document text."
    )
