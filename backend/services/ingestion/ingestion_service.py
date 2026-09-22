from services.chunking.chunk_validator import ChunkValidator
from services.chunking.chunker_factory import ChunkerFactory
from services.ingestion.loader_factory import LoaderFactory



class IngestionPipeline:
    """
    Orchestrates document ingestion.

    Pipeline:
        Load Document
            ↓
        Extract Text
            ↓
        Chunk Text
            ↓
        Validate Chunks
    """

    def __init__(
        self,
        chunker_type: str = "recursive",
        **loader_kwargs,
    ):
        self.chunker = ChunkerFactory.create(chunker_type)
        self.loader_kwargs = loader_kwargs

    def ingest(self, file_path: str):
        """
        Load a document and return validated chunks.
        """

        loader = LoaderFactory.create(
            file_path,
            **self.loader_kwargs,
        )

        document_text = loader.load()

        chunks = self.chunker.chunk(document_text)

        validated_chunks = ChunkValidator.validate(chunks)

        return validated_chunks
