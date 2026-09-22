from fastapi import APIRouter

from schemas.governance.audit_log import (
    AuditAction,
)
from services.governance.audit_service import (
    AuditService,
)

router = APIRouter(
    prefix="/governance",
    tags=["Governance"],
)

audit_service = AuditService()


@router.post("/audit")
async def create_audit_log(
    resource_type: str,
    resource_id: str,
    action: AuditAction,
    performed_by: str = "system",
    message: str = "",
):
    return audit_service.log(
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        performed_by=performed_by,
        message=message,
    )


@router.get("/audit")
async def get_audit_logs():
    return audit_service.get_logs()


@router.get("/audit/{resource_type}/{resource_id}")
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
):
    return audit_service.get_resource_logs(
        resource_type,
        resource_id,
    )
