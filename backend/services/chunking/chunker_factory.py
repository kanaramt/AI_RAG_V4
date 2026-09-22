from services.chunking.base_chunker import BaseChunker
from services.chunking.recursive_chunker import RecursiveChunker
from services.chunking.semantic_chunker import SemanticChunker
from services.chunking.token_chunker import TokenChunker


class ChunkerFactory:
    """
    Factory class for creating chunker instances.
    """

    @staticmethod
    def create(chunker_type: str, **kwargs) -> BaseChunker:
        """
        Create and return the requested chunker.

        Supported chunkers:
        - recursive
        - token
        - semantic
        """

        chunker_type = chunker_type.lower()

        if chunker_type == "recursive":
            return RecursiveChunker(**kwargs)

        if chunker_type == "token":
            return TokenChunker(**kwargs)

        if chunker_type == "semantic":
            return SemanticChunker(**kwargs)

        raise ValueError(
            f"Unsupported chunker type: {chunker_type}"
        )
