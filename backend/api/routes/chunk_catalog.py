from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db

from services.document_management.chunk_sql_repository import (
    ChunkSQLRepository,
)

router = APIRouter(
    tags=["Chunk Catalog"],
)


@router.get("/document-chunks/{document_id}")
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db),
):
    repository = ChunkSQLRepository(db)

    return repository.get_by_document_id(
        document_id
    )
