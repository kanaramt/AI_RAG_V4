from schemas.governance.audit_log import (
    AuditLog,
)


class AuditRepository:
    """
    Temporary in-memory audit repository.

    Future:
    - PostgreSQL
    - Elasticsearch
    """

    def __init__(self):

        self._logs: list[AuditLog] = []

    def create(
        self,
        log: AuditLog,
    ) -> AuditLog:

        self._logs.append(log)

        return log

    def get_all(
        self,
    ) -> list[AuditLog]:

        return self._logs

    def get_by_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[AuditLog]:

        return [
            log
            for log in self._logs
            if (
                log.resource_type == resource_type
                and log.resource_id == resource_id
            )
        ]
