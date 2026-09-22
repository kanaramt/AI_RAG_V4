from sqlalchemy.orm import Session

from database.models.ingestion_history import (
    IngestionHistoryModel,
)


class IngestionHistorySQLRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        document_id: str,
        asset_id: str | None,
        action: str,
        source_type: str | None,
        source_name: str | None,
        status: str,
        details_json: dict | None = None,
    ):

        model = IngestionHistoryModel(
            document_id=document_id,
            asset_id=asset_id,
            action=action,
            source_type=source_type,
            source_name=source_name,
            status=status,
            details_json=details_json,
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)

        return model
