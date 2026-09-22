from docx import Document

from services.ingestion.base_loader import BaseLoader


class DocxLoader(BaseLoader):
    """
    Loader for Microsoft Word (.docx) documents.
    """

    def load(self) -> str:
        """
        Extract text from a DOCX document.
        """

        if not self.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        document = Document(self.file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)
