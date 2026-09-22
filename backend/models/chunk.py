from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """
    Represents a single document chunk.
    """

    text: str

    chunk_id: str = ""

    document_id: str = ""

    sentence_count: int = 0

    token_count: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)
