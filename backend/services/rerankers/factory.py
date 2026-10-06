import os
from services.rerankers.base import BaseReranker
from services.rerankers.providers import LocalReranker, JinaReranker, CohereReranker

class RerankerFactory:
    @staticmethod
    def create() -> BaseReranker:
        provider = os.getenv("ACTIVE_RERANKER_PROVIDER", "local").lower()
        
        if provider == "jina":
            return JinaReranker()
        elif provider == "cohere":
            return CohereReranker()
        elif provider == "local":
            return LocalReranker()
        else:
            raise ValueError(f"Unsupported reranker provider: {provider}")
