from typing import Any

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """
    Represents the origin of a retrieved piece of information.
    Used for answer citations and source grounding.
    """

    document_id: str = Field(
        default="",
        description="Unique document identifier."
    )

    chunk_id: str = Field(
        default="",
        description="Unique chunk identifier."
    )

    source: str = Field(
        default="",
        description="Original file or URL."
    )

    page: int | None = Field(
        default=None,
        description="Page number if available."
    )

    section: str | None = Field(
        default=None,
        description="Document section or heading."
    )

    score: float = Field(
        default=0.0,
        description="Retrieval confidence score."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional source metadata."
    )
