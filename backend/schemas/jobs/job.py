from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from utils.datetime_utils import ist_now

class JobType(str, Enum):
    """
    Supported enterprise jobs.
    """

    EMBEDDING = "embedding"

    RE_EMBEDDING = "re_embedding"

    INDEXING = "indexing"

    OCR = "ocr"

    EXPORT = "export"

    DELETE = "delete"

    METADATA_UPDATE = "metadata_update"


class JobStatus(str, Enum):
    """
    Enterprise job status.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class Job(BaseModel):
    """
    Enterprise background job.
    """

    job_id: str = Field(default="")

    job_type: JobType

    status: JobStatus = JobStatus.PENDING

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    message: str = Field(default="")

    created_by: str = Field(default="system")

    created_at: datetime = Field(
        default_factory=ist_now
    )

    updated_at: datetime = Field(
        default_factory=ist_now
    )
