from catalog.schemas.knowledge_asset import (
    AssetStatus,
    KnowledgeAsset,
)


class AssetAnalytics:
    """
    Analytics for the Knowledge Catalog.
    """

    def summary(
        self,
        assets: list[KnowledgeAsset],
    ) -> dict:

        total_assets = len(assets)

        active_assets = sum(
            1
            for asset in assets
            if asset.status == AssetStatus.ACTIVE
        )

        draft_assets = sum(
            1
            for asset in assets
            if asset.status == AssetStatus.DRAFT
        )

        archived_assets = sum(
            1
            for asset in assets
            if asset.status == AssetStatus.ARCHIVED
        )

        deleted_assets = sum(
            1
            for asset in assets
            if asset.status == AssetStatus.DELETED
        )

        average_health = (
            sum(
                asset.health_score
                for asset in assets
            ) / total_assets
            if total_assets
            else 0.0
        )

        total_chunks = sum(
            asset.chunk_count
            for asset in assets
        )

        average_chunks = (
            total_chunks / total_assets
            if total_assets
            else 0.0
        )

        source_types = {}

        for asset in assets:

            source = asset.source_type.value

            source_types[source] = (
                source_types.get(source, 0) + 1
            )

        return {

            "total_assets": total_assets,

            "active_assets": active_assets,

            "draft_assets": draft_assets,

            "archived_assets": archived_assets,

            "deleted_assets": deleted_assets,

            "average_health_score": round(
                average_health,
                2,
            ),

            "total_chunks": total_chunks,

            "average_chunks_per_asset": round(
                average_chunks,
                2,
            ),

            "source_types": source_types,
        }
