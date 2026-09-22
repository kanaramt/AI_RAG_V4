from schemas.retrieval.retrieved_document import RetrievedDocument


class ScoreFusion:
    """
    Reciprocal Rank Fusion (RRF)
    """

    def __init__(
        self,
        k: int = 60,
    ):
        self.k = k

    def fuse(
        self,
        dense_results: list[RetrievedDocument],
        sparse_results: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:

        fused_scores = {}
        document_lookup = {}

        for rank, document in enumerate(dense_results):

            score = 1 / (self.k + rank + 1)

            fused_scores[document.id] = (
                fused_scores.get(document.id, 0)
                + score
            )

            document_lookup[document.id] = document

        for rank, document in enumerate(sparse_results):

            score = 1 / (self.k + rank + 1)

            fused_scores[document.id] = (
                fused_scores.get(document.id, 0)
                + score
            )

            document_lookup[document.id] = document

        ranked_documents = sorted(
            fused_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            document_lookup[doc_id]
            for doc_id, _ in ranked_documents
        ]
