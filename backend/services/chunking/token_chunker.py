import tiktoken

from services.chunking.base_chunker import BaseChunker


class TokenChunker(BaseChunker):
    """
    Chunks text using LLM tokens.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",
    ):

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.encoding = tiktoken.get_encoding(
            encoding_name
        )

    def chunk(
        self,
        text: str,
    ) -> list[str]:

        tokens = self.encoding.encode(text)

        chunks = []

        step = self.chunk_size - self.chunk_overlap

        for i in range(
            0,
            len(tokens),
            step,
        ):

            chunk_tokens = tokens[
                i : i + self.chunk_size
            ]

            chunks.append(
                self.encoding.decode(chunk_tokens)
            )

        return chunks
