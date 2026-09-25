import os

from huggingface_hub import InferenceClient

from services.embeddings.base_embedding import BaseEmbedding


class HuggingFaceHostedEmbedding(BaseEmbedding):
    """Hugging Face hosted Feature Extraction provider."""

    def __init__(self, model_name: str, api_key: str | None = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")

        if not self.api_key:
            raise RuntimeError(
                f"Hugging Face token is required for embedding model "
                f"'{self.model_name}'."
            )

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=self.api_key,
        )

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        result = self.client.feature_extraction(
            texts,
            model=self.model_name,
        )

        return result.tolist()