from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ChunkSchema(BaseModel):

    chunk_id: str

    document_id: str

    chunk_index: int

    content: str

    metadata: dict[str, Any] = {}

    created_at: datetime
