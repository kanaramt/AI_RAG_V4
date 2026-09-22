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

    _easyocr_reader = None

    @classmethod
    def get_easyocr_reader(cls):
        if cls._easyocr_reader is None:
            import easyocr
            print("Initializing EasyOCR Reader (gpu=False)...")
            cls._easyocr_reader = easyocr.Reader(["en"], gpu=False)
        return cls._easyocr_reader

    def __init__(
        self,
        file_path: str,
        engine: str = "auto",
    ):
        super().__init__(file_path)
        self.engine = engine.lower()

    def _validate_image(self) -> Image.Image:
        """
        Open and validate the image.
        """

        if not self.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        image = Image.open(self.file_path)
        image.verify()

        return Image.open(self.file_path)

    def _easyocr(self, image: Image.Image) -> str:
        """
        OCR using EasyOCR.
        """
        reader = self.get_easyocr_reader()
        results = reader.readtext(image)

        return "\n".join(
            text for _, text, _ in results
        )

    def _tesseract(self, image: Image.Image) -> str:
        """
        OCR using Tesseract.
        """
        import pytesseract
        return pytesseract.image_to_string(image)

    def load(self) -> str:
        """
        Extract text from an image.
        """

        image = self._validate_image()

        if self.engine == "easyocr":
            return self._easyocr(image)

        if self.engine == "tesseract":
            return self._tesseract(image)

        if self.engine == "auto":
            try:
                text = self._easyocr(image)

                if text.strip():
                    return text

            except Exception:
                pass

            text = self._tesseract(image)

            if text.strip():
                return text

            raise RuntimeError(
                "OCR failed using both EasyOCR and Tesseract."
            )

        raise ValueError(
            f"Unsupported OCR engine: {self.engine}"
        )
