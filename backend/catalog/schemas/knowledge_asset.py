from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from backend.utils.datetime_utils import ist_now

class AssetStatus(str, Enum):
    """
    Lifecycle status of a knowledge asset.
    """

    DRAFT = "draft"
    INDEXING = "indexing"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class SourceType(str, Enum):
    """
    Supported knowledge sources.
    """

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    URL = "url"
    HTML = "html"
    CSV = "csv"
    XLSX = "xlsx"
    IMAGE = "image"
    API = "api"
    DATABASE = "database"
    WEBSITE = "website"
    OTHER = "other"


class KnowledgeAsset(BaseModel):
    """
    Master entity representing a knowledge asset.
    """

    asset_id: str = ""

    document_id: str = ""

    source_type: SourceType

    source_name: str = ""

    source_path: str = ""

    title: str = ""

    owner: str = ""

    department: str = ""

    tags: list[str] = Field(
        default_factory=list
    )

    language: str = "en"

    chunk_count: int = 0

    embedding_model: str = ""

    vector_store: str = ""

    metadata: dict[str, Any] = {}

    status: AssetStatus = AssetStatus.DRAFT

    version: int = 1

    health_score: float = 0.0

    created_at: datetime = Field(
        default_factory=ist_now
    )

    updated_at: datetime = Field(
        default_factory=ist_now
    )