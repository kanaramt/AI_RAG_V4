from pathlib import Path
from services.ingestion.base_loader import BaseLoader
from services.ingestion.csv_loader import CSVLoader
from services.ingestion.docx_loader import DocxLoader
from services.ingestion.excel_loader import ExcelLoader
from services.ingestion.image_loader import ImageLoader
from services.ingestion.markdown_loader import MarkdownLoader
from services.ingestion.pdf_loader import PDFLoader
from services.ingestion.text_loader import TextLoader


from services.ingestion.web_loader import WebLoader


class LoaderFactory:
    """
    Factory class for creating the correct loader
    based on file extension or URL scheme.
    """

    _LOADERS = {
        ".pdf": PDFLoader,
        ".txt": TextLoader,
        ".docx": DocxLoader,
        ".md": MarkdownLoader,
        ".markdown": MarkdownLoader,
        ".csv": CSVLoader,
        ".xlsx": ExcelLoader,
        ".xls": ExcelLoader,
        ".png": ImageLoader,
        ".jpg": ImageLoader,
        ".jpeg": ImageLoader,
        ".webp": ImageLoader,
        ".bmp": ImageLoader,
        ".tiff": ImageLoader,
    }

    @classmethod
    def create(
        cls,
        file_path: str,
        **kwargs,
    ) -> Any:
        """
        Return the appropriate loader based on file extension or URL scheme.
        """
        path_str = str(file_path).strip()
        if path_str.startswith("http://") or path_str.startswith("https://"):
            return WebLoader(path_str, **kwargs)

        extension = Path(file_path).suffix.lower()

        loader_class = cls._LOADERS.get(extension)

        if loader_class is None:
            raise ValueError(
                f"Unsupported file type or resource: {extension}"
            )

        return loader_class(file_path, **kwargs)
