from models.chunk import Chunk
from services.chunking.similarity import Similarity


class ChunkValidator:
    """
    Validates and improves chunks before indexing.
    """

    def __init__(
        self,
        min_sentences: int = 2,
        max_sentences: int = 8,
    ):
        self.min_sentences = min_sentences
        self.max_sentences = max_sentences

    def remove_empty_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:
        return [
            chunk
            for chunk in chunks
            if chunk.text.strip()
        ]

    def merge_small_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:
        """
        Merge small chunks with the previous chunk.

        Temporary implementation until semantic merge
        is added later.
        """

        if not chunks:
            return chunks

        merged = [chunks[0]]

        for chunk in chunks[1:]:

            if chunk.sentence_count < self.min_sentences:

                previous = merged[-1]

                previous.text = (
                    previous.text + " " + chunk.text
                ).strip()

                previous.sentence_count += chunk.sentence_count

            else:
                merged.append(chunk)

        return merged

    def validate(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        chunks = self.remove_empty_chunks(chunks)
        chunks = self.merge_small_chunks(chunks)

        return chunks
