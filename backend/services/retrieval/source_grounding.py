from schemas.retrieval.retrieved_document import RetrievedDocument
from schemas.retrieval.source_reference import SourceReference


class SourceGroundingService:
    """
    Builds source references from retrieved documents.

    Responsibilities
    ----------------
    • Generate citations
    • Remove duplicate sources
    • Sort by retrieval confidence
    """

    def build(
        self,
        documents: list[RetrievedDocument],
    ) -> list[SourceReference]:

        sources: list[SourceReference] = []

        seen = set()

        for document in documents:

            source = SourceReference(

                document_id=document.metadata.get(
                    "doc_id",
                    ""
                ),

                chunk_id=document.metadata.get(
                    "chunk_id",
                    document.id,
                ),

                source=document.source,

                page=document.page,

                section=document.metadata.get(
                    "section"
                ),

                score=document.score,

                metadata=document.metadata,
            )

            key = (
                source.document_id,
                source.chunk_id,
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(source)

        sources.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return sources
