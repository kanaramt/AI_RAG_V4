from fastapi import APIRouter, HTTPException

from services.versioning.version_service import (
    VersionService,
)

router = APIRouter(
    prefix="/versions",
    tags=["Versioning"],
)

version_service = VersionService()


@router.post("/{document_id}")
async def create_version(
    document_id: str,
    created_by: str = "system",
    change_summary: str = "",
):
    return version_service.create_version(
        document_id=document_id,
        created_by=created_by,
        change_summary=change_summary,
    )


@router.get("/{document_id}")
async def get_versions(
    document_id: str,
):
    return version_service.get_versions(
        document_id
    )


@router.get("/{document_id}/latest")
async def get_latest_version(
    document_id: str,
):
    version = version_service.get_latest(
        document_id
    )

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="No versions found.",
        )

    return version


@router.put("/{version_id}/activate")
async def activate_version(
    version_id: str,
):
    success = version_service.activate_version(
        version_id
    )

    return {
        "success": success,
    }
