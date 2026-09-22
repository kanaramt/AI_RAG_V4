from sqlalchemy.orm import Session

from catalog.schemas.knowledge_asset import (
    AssetStatus,
    KnowledgeAsset,
    SourceType,
)
from database.models.knowledge_asset import (
    KnowledgeAssetModel,
)


class AssetSQLRepository:
    """
    SQLAlchemy repository for Knowledge Assets.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        asset: KnowledgeAsset,
    ) -> KnowledgeAsset:

        model = KnowledgeAssetModel(
            asset_id=asset.asset_id,
            document_id=asset.document_id,
            source_type=asset.source_type.value,
            source_name=asset.source_name,
            source_path=asset.source_path,
            title=asset.title,
            owner=asset.owner,
            department=asset.department,
            tags=",".join(asset.tags),
            language=asset.language,
            chunk_count=asset.chunk_count,
            embedding_model=asset.embedding_model,
            vector_store=asset.vector_store,
            metadata_json=asset.metadata,
            status=asset.status.value,
            version=asset.version,
            health_score=asset.health_score,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return asset

    def get_all(
        self,
    ) -> list[KnowledgeAsset]:

        models = self.db.query(
            KnowledgeAssetModel
        ).all()

        return [
            self._to_schema(model)
            for model in models
        ]

    def get(
        self,
        asset_id: str,
    ) -> KnowledgeAsset | None:

        model = (
            self.db.query(KnowledgeAssetModel)
            .filter(
                KnowledgeAssetModel.asset_id == asset_id
            )
            .first()
        )

        if model is None:
            return None

        return self._to_schema(model)

    def get_by_document_id(
        self,
        document_id: str,
    ) -> KnowledgeAsset | None:

        model = (
            self.db.query(KnowledgeAssetModel)
            .filter(
                KnowledgeAssetModel.document_id == document_id
            )
            .first()
        )

        if model is None:
            return None

        return self._to_schema(model)

    def update(
        self,
        asset: KnowledgeAsset,
    ) -> KnowledgeAsset:

        model = (
            self.db.query(KnowledgeAssetModel)
            .filter(
                KnowledgeAssetModel.asset_id == asset.asset_id
            )
            .first()
        )

        if model is None:
            raise ValueError(
                "Knowledge asset not found."
            )

        model.document_id = asset.document_id
        model.source_path = asset.source_path
        model.chunk_count = asset.chunk_count
        model.embedding_model = asset.embedding_model
        model.vector_store = asset.vector_store
        model.metadata_json = asset.metadata
        model.status = asset.status.value
        model.version = asset.version
        model.health_score = asset.health_score
        model.updated_at = asset.updated_at

        self.db.commit()

        return asset

    def delete(
        self,
        asset_id: str,
    ) -> bool:

        model = (
            self.db.query(KnowledgeAssetModel)
            .filter(
                KnowledgeAssetModel.asset_id == asset_id
            )
            .first()
        )

        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()

        return True

    def clear(
        self,
    ):

        self.db.query(
            KnowledgeAssetModel
        ).delete()

        self.db.commit()

    def _to_schema(
        self,
        model: KnowledgeAssetModel,
    ) -> KnowledgeAsset:

        return KnowledgeAsset(
            asset_id=model.asset_id,
            document_id=model.document_id,
            source_type=SourceType(model.source_type),
            source_name=model.source_name,
            source_path=model.source_path,
            title=model.title,
            owner=model.owner,
            department=model.department,
            tags=model.tags.split(",")
            if model.tags
            else [],
            language=model.language,
            chunk_count=model.chunk_count,
            embedding_model=model.embedding_model,
            vector_store=model.vector_store,
            metadata=model.metadata_json or {},
            status=AssetStatus(model.status),
            version=model.version,
            health_score=model.health_score,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
