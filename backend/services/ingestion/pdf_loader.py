from pypdf import PdfReader

from services.ingestion.base_loader import BaseLoader


class PDFLoader(BaseLoader):
    """
    Loader for PDF documents.
    """

    def load(self) -> str:
        """
        Extract text from all pages of the PDF.
        """

        if not self.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        reader = PdfReader(self.file_path)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)
