from catalog.schemas.knowledge_asset import (
    KnowledgeAsset,
)


class AssetSearch:
    """
    Enterprise Knowledge Asset Search.
    """

    def search(
        self,
        assets: list[KnowledgeAsset],
        query: str,
    ) -> list[KnowledgeAsset]:

        query = query.lower().strip()

        if not query:
            return assets

        results: list[KnowledgeAsset] = []

        for asset in assets:

            searchable_text = " ".join(
                [
                    asset.title,
                    asset.source_name,
                    asset.owner,
                    asset.department,
                    " ".join(asset.tags),
                ]
            ).lower()

            if query in searchable_text:
                results.append(asset)

        return results
