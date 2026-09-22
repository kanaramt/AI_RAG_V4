from schemas.retrieval.retrieved_document import RetrievedDocument


class MetadataFilter:
    """
    Filters retrieved documents using metadata.
    """

    def filter(
        self,
        documents: list[RetrievedDocument],
        filters: dict,
    ) -> list[RetrievedDocument]:

        if not filters:
            return documents

        filtered_documents = []

        for document in documents:

            metadata = document.metadata or {}

            matched = True

            for key, value in filters.items():

                if metadata.get(key) != value:
                    matched = False
                    break

            if matched:
                filtered_documents.append(document)

        return filtered_documents
