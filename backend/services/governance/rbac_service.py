from schemas.governance.rbac import (
    Permission,
    RoleAssignment,
    UserRole,
)


class RBACService:
    """
    Enterprise RBAC Service.
    """

    DEFAULT_PERMISSIONS = {

        UserRole.SUPER_ADMIN: list(Permission),

        UserRole.ADMIN: [
            Permission.READ,
            Permission.WRITE,
            Permission.DELETE,
            Permission.APPROVE,
            Permission.EXPORT,
        ],

        UserRole.AI_ENGINEER: [
            Permission.READ,
            Permission.WRITE,
            Permission.EXPORT,
        ],

        UserRole.REVIEWER: [
            Permission.READ,
            Permission.APPROVE,
        ],

        UserRole.ANALYST: [
            Permission.READ,
            Permission.EXPORT,
        ],

        UserRole.VIEWER: [
            Permission.READ,
        ],
    }

    def assign_role(
        self,
        username: str,
        role: UserRole,
    ) -> RoleAssignment:

        return RoleAssignment(
            username=username,
            role=role,
            permissions=self.DEFAULT_PERMISSIONS[
                role
            ],
        )

    def has_permission(
        self,
        assignment: RoleAssignment,
        permission: Permission,
    ) -> bool:

        return permission in assignment.permissions
