
import uuid
from datetime import datetime

from catalog.repositories.asset_sql_repository import (
    AssetSQLRepository,
)

from catalog.analytics.asset_analytics import (
    AssetAnalytics,
)
from catalog.repositories.asset_repository import (
    AssetRepository,
)
from catalog.repositories.asset_sql_repository import (
    AssetSQLRepository,
)
from catalog.schemas.knowledge_asset import (
    AssetStatus,
    KnowledgeAsset,
    SourceType,
)
from catalog.search.asset_search import (
    AssetSearch,
)
from utils.datetime_utils import ist_now

class AssetService:
    """
    Enterprise Knowledge Asset Service.
    """

    def __init__(
    self,
    repository=None,
    ):

        self.repository = (
            repository
            if repository is not None
            else AssetRepository()
        )

        self.search_engine = AssetSearch()

        self.analytics = AssetAnalytics()

    def create_asset(
        self,
        source_type: SourceType,
        source_name: str,
        title: str,
        owner: str = "",
        department: str = "",
        tags: list[str] | None = None,
    ) -> KnowledgeAsset:

        asset = KnowledgeAsset(

            asset_id=str(uuid.uuid4()),

            document_id=str(uuid.uuid4()),

            source_type=source_type,

            source_name=source_name,

            title=title,

            owner=owner,

            department=department,

            tags=tags or [],

            status=AssetStatus.DRAFT,
        )

        return self.repository.create(asset)

    def get_assets(
        self,
    ) -> list[KnowledgeAsset]:

        return self.repository.get_all()

    def get_asset(
        self,
        asset_id: str,
    ) -> KnowledgeAsset | None:

        return self.repository.get(asset_id)

    def update_asset(
        self,
        asset: KnowledgeAsset,
    ) -> KnowledgeAsset:

        asset.updated_at = ist_now()

        return self.repository.update(asset)

    def delete_asset(
        self,
        asset_id: str,
    ) -> bool:

        return self.repository.delete(asset_id)

    def search_assets(
        self,
        query: str,
    ) -> list[KnowledgeAsset]:

        return self.search_engine.search(
            self.repository.get_all(),
            query,
        )

    def get_analytics(
        self,
    ) -> dict:

        return self.analytics.summary(
            self.repository.get_all(),
        )
