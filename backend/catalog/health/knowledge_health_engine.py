from catalog.schemas.knowledge_asset import (
    KnowledgeAsset,
)


class KnowledgeHealthEngine:
    """
    Calculates health score for Knowledge Assets.
    """

    @staticmethod
    def calculate_health_score(
        asset: KnowledgeAsset,
    ) -> float:

        score = 0.0

        if asset.status.value == "active":
            score += 40

        if asset.chunk_count > 0:
            score += 30

        if asset.embedding_model:
            score += 30

        return min(score, 100.0)
