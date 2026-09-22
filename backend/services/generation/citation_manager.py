from schemas.retrieval.retrieved_document import RetrievedDocument


class CitationManager:
    """
    Builds citations from retrieved documents.
    """

    def build(
        self,
        documents: list[RetrievedDocument],
    ) -> list[dict]:

        citations = []

        for document in documents:

            citations.append(
                {
                    "id": document.id,
                    "source": document.source,
                    "page": document.page,
                }
            )

        return citations
