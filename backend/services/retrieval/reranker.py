from settings import settings
from schemas.retrieval.retrieved_document import RetrievedDocument


class Reranker:
    """
    Cross-Encoder Reranker
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            print(f"[LazyLoad] Initializing CrossEncoder reranker ({settings.RERANKER_MODEL})...")
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(settings.RERANKER_MODEL)
        return self._model

    def rerank(
        self,
        query: str,
        documents: list[RetrievedDocument],
        top_k: int = 3,
    ) -> list[RetrievedDocument]:
        # top_k: strictly enforced max number of chunks returned.
        # This directly controls LLM token cost — fewer chunks = fewer prompt tokens.

        if not documents:
            return []

        sentence_pairs = [
            (query, document.text)
            for document in documents
        ]

        scores = self.model.predict(
            sentence_pairs
        )

        for document, score in zip(
            documents,
            scores,
        ):
            document.score = float(score)

        # Filter out completely irrelevant chunks (score < 0.3)
        documents = [doc for doc in documents if doc.score >= 0.3]

        documents.sort(
            key=lambda document: document.score,
            reverse=True,
        )

        # STRICT CAP: return at most top_k chunks.
        # Every extra chunk beyond top_k is sent to the LLM and costs real tokens.
        return documents[:top_k]
