from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DocumentSchema(BaseModel):

    document_id: str

    title: str

    source_type: str

    source_name: str

    metadata: dict[str, Any] = {}

    content: str

    created_at: datetime
