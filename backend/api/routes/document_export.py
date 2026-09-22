from fastapi import APIRouter
from fastapi.responses import FileResponse

from services.document_management.json_export_service import (
    JSONExportService,
)

router = APIRouter(
    prefix="/export",
    tags=["Dataset Export"],
)


@router.get(
    "/knowledge-base"
)
def export_knowledge_base():

    service = JSONExportService()

    file_path = (
        service.export_all_documents(
            "exports/knowledge_base.json"
        )
    )

    return FileResponse(
        path=file_path,

        filename="knowledge_base.json",
        media_type="application/json",
    )
