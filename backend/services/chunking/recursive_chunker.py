
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.chunking.base_chunker import BaseChunker


class RecursiveChunker(BaseChunker):
    """
    Production-grade recursive character chunker.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def chunk(
        self,
        text: str,
    ) -> list[str]:

        return self.splitter.split_text(text)
