from settings import settings

from services.vector_store.hybrid_service import HybridVectorStore


class VectorStoreFactory:
    """
    Factory responsible for creating the configured
    Vector Store implementation.
    """

    @staticmethod
    def create():

        provider = settings.VECTOR_STORE.lower()

        registry = {
            "hybrid": HybridVectorStore,
        }

        if provider not in registry:
            raise ValueError(
                f"Unsupported Vector Store: {provider}"
            )

        return registry[provider]()
