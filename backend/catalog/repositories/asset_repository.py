from catalog.schemas.knowledge_asset import (
    KnowledgeAsset,
)


class AssetRepository:
    """
    Shared in-memory repository.

    Future:
    Replace with SQLAlchemy implementation.
    """

    _instance = None
    _assets: list[KnowledgeAsset] = []

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def create(
        self,
        asset: KnowledgeAsset,
    ) -> KnowledgeAsset:

        self._assets.append(asset)
        
        return asset

    def get_all(
        self,
    ) -> list[KnowledgeAsset]:

        

        return self._assets

    def get(
        self,
        asset_id: str,
    ) -> KnowledgeAsset | None:

        for asset in self._assets:

            if asset.asset_id == asset_id:

                return asset

        return None

    def get_by_document_id(
        self,
        document_id: str,
    ) -> KnowledgeAsset | None:

        for asset in self._assets:

            if asset.document_id == document_id:

                return asset

        return None

    def update(
        self,
        asset: KnowledgeAsset,
    ) -> KnowledgeAsset:

        for index, existing in enumerate(
            self._assets
        ):

            if existing.asset_id == asset.asset_id:

                self._assets[index] = asset

                return asset

        raise ValueError(
            "Knowledge asset not found."
        )

    def delete(
        self,
        asset_id: str,
    ) -> bool:

        for index, asset in enumerate(
            self._assets
        ):

            if asset.asset_id == asset_id:

                del self._assets[index]

                return True

        return False

    def clear(
        self,
    ):

        self._assets.clear()
