from services.embeddings.base_embedding import BaseEmbedding


class HuggingFaceEmbedding(BaseEmbedding):
    """
    Local Hugging Face embedding provider using sentence-transformers.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            # pyrefly: ignore [missing-import]
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_name,
                device="cpu",
            )
        return self._model

    def generate_embedding(self, text: str) -> list[float]:
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
        )

        return embeddings.tolist()