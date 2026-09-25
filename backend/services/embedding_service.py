import os
from typing import List

from settings import settings
from services.embeddings.embedding_registry import (
    DEFAULT_EMBEDDING_MODEL,
    get_embedding_model,
)
from services.embeddings.ollama_embedding import OllamaEmbedding
from services.embeddings.huggingface_embedding import HuggingFaceEmbedding
from services.embeddings.openai_embedding import OpenAIEmbedding
from services.embeddings.gemini_embedding import GeminiEmbedding
from services.embeddings.huggingface_hosted_embedding import HuggingFaceHostedEmbedding


class EmbeddingService:
    """
    Dynamic embedding service.

    The selected model determines the provider through
    EMBEDDING_MODEL_MAP.
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
    ):
        self.model = (
            model_name
            or os.getenv("ACTIVE_EMBEDDING_MODEL")
            or settings.EMBEDDING_MODEL
            or DEFAULT_EMBEDDING_MODEL
        )

        self.api_key = api_key

        self.model_config = get_embedding_model(self.model)
        self.provider_name = self.model_config["provider"]
        self.dimension = self.model_config["dimension"]

        self.provider = self._create_provider()

    def _create_provider(self):
        if self.provider_name == "ollama":
            return OllamaEmbedding(self.model)

        if self.provider_name == "huggingface_local":
            return HuggingFaceEmbedding(self.model)

        if self.provider_name == "openai":
            return OpenAIEmbedding(
                model_name=self.model,
                api_key=self.api_key,
            )

        if self.provider_name == "gemini":
            return GeminiEmbedding(
                model_name=self.model,
                api_key=self.api_key,
            )

        if self.provider_name == "huggingface_hosted":
            return HuggingFaceHostedEmbedding(
                model_name=self.model,
                api_key=self.api_key,
            )

        raise ValueError(
            f"Unsupported embedding provider '{self.provider_name}' "
            f"for model '{self.model}'."
        )

    def generate_embedding(self, text: str) -> List[float]:
        return self.provider.generate_embedding(text)

    def generate_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        return self.provider.generate_embeddings(texts)