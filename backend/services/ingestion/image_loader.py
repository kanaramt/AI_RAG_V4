from PIL import Image

from services.ingestion.base_loader import BaseLoader


class ImageLoader(BaseLoader):
    """
    Enterprise Image Loader.

    Supported OCR engines:
        - auto (default)
        - easyocr
        - tesseract
    """

    def __init__(
        self,
        file_path: str,
    ):
        super().__init__(file_path)

    def _validate_image(self) -> str:
        if not self.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        return self.file_path

    def load(self) -> str:
        """
        Extract text from an image using the OCR Factory.
        """
        self._validate_image()
        
        import cv2
        img = cv2.imread(self.file_path)
        if img is None:
            return ""
            
        from services.ocr.factory import OCRFactory
        reader = OCRFactory.create()
        return reader.extract_text(img)
