from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from utils.datetime_utils import ist_now

class VersionStatus(str, Enum):
    """
    Document version lifecycle.
    """

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentVersion(BaseModel):
    """
    Enterprise document version.
    """

    version_id: str = Field(default="")

    document_id: str = Field(default="")

    version_number: int = 1

    status: VersionStatus = VersionStatus.DRAFT

    created_by: str = Field(default="system")

    change_summary: str = Field(default="")

    created_at: datetime = Field(
        default_factory=ist_now
    )
    activated_at: datetime | None = None
