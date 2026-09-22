import uuid

from schemas.governance.audit_log import (
    AuditAction,
    AuditLog,
)
from services.governance.audit_repository import (
    AuditRepository,
)


class AuditService:
    """
    Enterprise Audit Service.
    """

    def __init__(self):

        self.repository = AuditRepository()

    def log(
        self,
        resource_type: str,
        resource_id: str,
        action: AuditAction,
        performed_by: str = "system",
        message: str = "",
    ) -> AuditLog:

        audit = AuditLog(

            audit_id=str(uuid.uuid4()),

            resource_type=resource_type,

            resource_id=resource_id,

            action=action,

            performed_by=performed_by,

            message=message,
        )

        return self.repository.create(audit)

    def get_logs(
        self,
    ) -> list[AuditLog]:

        return self.repository.get_all()

    def get_resource_logs(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[AuditLog]:

        return self.repository.get_by_resource(
            resource_type,
            resource_id,
        )
