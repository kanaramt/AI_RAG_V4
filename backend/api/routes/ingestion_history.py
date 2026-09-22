from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from database.models.ingestion_history import (
    IngestionHistoryModel,
)

router = APIRouter()


@router.get(
    "/ingestion-history",
    tags=["Ingestion History"],
)
def get_ingestion_history(
    db: Session = Depends(get_db),
):
    records = (
        db.query(IngestionHistoryModel)
        .order_by(
            IngestionHistoryModel.id.desc()
        )
        .all()
    )

    return records
