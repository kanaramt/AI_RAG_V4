from schemas.retrieval.retrieved_document import RetrievedDocument
from services.retrieval.context_compressor import ContextCompressor


class ContextBuilder:
    """
    Builds the final LLM context from retrieved documents.

    Pipeline
    --------
    Documents
        ↓
    Merge
        ↓
    Compress
        ↓
    Final Context
    """

    def __init__(self):
        self.compressor = ContextCompressor()

    async def build(
        self,
        query: str,
        documents: list[RetrievedDocument],
    ) -> str:

        contexts = []

        for document in documents:
            contexts.append(document.text)

        merged_context = "\n\n".join(contexts)

        compressed_context = await self.compressor.compress(
            query=query,
            context=merged_context,
        )

        return compressed_context
