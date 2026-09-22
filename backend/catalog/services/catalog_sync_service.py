from pathlib import Path

from catalog.repositories.asset_sql_repository import (
    AssetSQLRepository,
)
from catalog.schemas.knowledge_asset import (
    AssetStatus,
    SourceType,
)
from catalog.services.asset_service import (
    AssetService,
)
from catalog.health.knowledge_health_engine import (
    KnowledgeHealthEngine,
)
from database.session import SessionLocal


class CatalogSyncService:
    """
    Synchronizes ingested documents with the Knowledge Catalog.
    """

    def sync_document(
        self,
        doc_id: str,
        source_name: str,
        source_path: str,
        chunk_count: int,
        embedding_model: str,
        vector_store: str,
    ):
        db = SessionLocal()
        try:
            asset_service = AssetService(AssetSQLRepository(db))

            asset = asset_service.repository.get_by_document_id(
                doc_id
            )

            if asset is None:
                extension = Path(source_name).suffix.lower()

                source_type = {
                    ".pdf": SourceType.PDF,
                    ".docx": SourceType.DOCX,
                    ".txt": SourceType.TXT,
                    ".csv": SourceType.CSV,
                    ".xlsx": SourceType.XLSX,
                    ".html": SourceType.HTML,
                    ".url": SourceType.URL,
                }.get(
                    extension,
                    SourceType.OTHER,
                )

                asset = asset_service.create_asset(
                    source_type=source_type,
                    source_name=source_name,
                    title=source_name,
                )

            asset.document_id = doc_id
            asset.source_path = source_path
            asset.chunk_count = chunk_count
            asset.embedding_model = embedding_model
            asset.vector_store = vector_store
            asset.status = AssetStatus.ACTIVE

            asset.health_score = (
                KnowledgeHealthEngine.calculate_health_score(
                    asset
                )
            )

            return asset_service.update_asset(asset)
        finally:
            db.close()
