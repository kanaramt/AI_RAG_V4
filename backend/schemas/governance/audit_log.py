from datetime import datetime
from enum import Enum
from backend.utils.datetime_utils import ist_now
from pydantic import BaseModel, Field


class AuditAction(str, Enum):
    """
    Supported governance actions.
    """

    CREATE = "create"

    UPDATE = "update"

    DELETE = "delete"

    APPROVE = "approve"

    REJECT = "reject"

    EXPORT = "export"

    LOGIN = "login"

    LOGOUT = "logout"


class AuditLog(BaseModel):
    """
    Enterprise audit log.
    """

    audit_id: str = Field(default="")

    resource_type: str = Field(default="")

    resource_id: str = Field(default="")

    action: AuditAction

    performed_by: str = Field(default="system")

    message: str = Field(default="")

    created_at: datetime = Field(
        default_factory=ist_now
    )