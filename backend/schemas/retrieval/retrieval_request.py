from typing import Any

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    """
    Request object passed to the retrieval engine.
    """

    query: str = Field(
        description="User search query."
    )

    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of documents to retrieve."
    )

    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata filters."
    )
