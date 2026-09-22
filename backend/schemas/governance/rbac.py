from enum import Enum

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """
    Enterprise user roles.
    """

    SUPER_ADMIN = "super_admin"

    ADMIN = "admin"

    AI_ENGINEER = "ai_engineer"

    REVIEWER = "reviewer"

    ANALYST = "analyst"

    VIEWER = "viewer"


class Permission(str, Enum):
    """
    Supported permissions.
    """

    READ = "read"

    WRITE = "write"

    DELETE = "delete"

    APPROVE = "approve"

    EXPORT = "export"

    MANAGE_USERS = "manage_users"


class RoleAssignment(BaseModel):
    """
    Maps a user to a role.
    """

    username: str = Field(...)

    role: UserRole

    permissions: list[Permission] = Field(
        default_factory=list
    )
