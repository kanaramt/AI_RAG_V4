from typing import List


class DocumentChunker:
    """
    Splits extracted document text into smaller chunks.

    This is the first implementation.
    Later we will replace it with LangChain's
    RecursiveCharacterTextSplitter.
    """

    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 400

    @classmethod
    def chunk_text(cls, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        """

        if not text.strip():
            return []

        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:

            end = min(start + cls.CHUNK_SIZE, text_length)

            chunks.append(text[start:end])

            if end == text_length:
                break

            start = end - cls.CHUNK_OVERLAP

        return chunks
