class Chunker:
    """
    Splits text into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        text: str,
    ) -> list[str]:

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunks.append(
                text[start:end]
            )

            start += (
                self.chunk_size
                - self.chunk_overlap
            )

        return chunks
