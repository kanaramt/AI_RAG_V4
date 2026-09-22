from pathlib import Path
from fastapi import HTTPException, UploadFile
from backend.services.document_extractor import DocumentExtractor


class DocumentIntelligence:
    """
    Enterprise Document Intelligence Service.

    Responsibilities
    ----------------
    • Read documents
    • OCR images
    • Analyse images
    • Extract metadata
    • Route files to the correct processor

    Future:
    • Tables
    • Charts
    • Diagrams
    • Forms
    • Vision Models
    """

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".webp",
    }

    DOCUMENT_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".doc",
        ".txt",
        ".csv",
        ".xlsx",
        ".xls",
        ".pptx",
        ".ppt",
        ".json",
    }

    
    _reader = None

    @classmethod
    def get_reader(cls):
        if cls._reader is None:
            import easyocr
            print("Initializing EasyOCR Reader (gpu=False)...")
            cls._reader = easyocr.Reader(["en"], gpu=False)
        return cls._reader

    @classmethod
    def is_image(cls, file_name: str) -> bool:
        return Path(file_name).suffix.lower() in cls.IMAGE_EXTENSIONS

    @classmethod
    def is_document(cls, file_name: str) -> bool:
        return Path(file_name).suffix.lower() in cls.DOCUMENT_EXTENSIONS

    @classmethod
    def extract_text_from_image(cls, image_path: str) -> str:
        """
        Extract text from an image using OCR.
        """
        reader = cls.get_reader()
        results = reader.readtext(image_path)

        extracted_text = " ".join(
            text for _, text, _ in results
        )

        return extracted_text.strip()
        
    @classmethod
    async def extract_text(
        cls,
        file: UploadFile,
    ) -> str:
        """
        Unified entry point for every uploaded file.

        Documents -> DocumentExtractor
        Images -> OCR
        """

        if cls.is_document(file.filename):
            return await DocumentExtractor.extract_text(file)

        if cls.is_image(file.filename):
            import numpy as np
            import cv2
            
            contents = await file.read()
            await file.seek(0)
            
            # Decode the image from memory bytes directly
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not decode image: {file.filename}"
                )

            # Perform EasyOCR extraction
            reader = cls.get_reader()
            results = reader.readtext(img)
            extracted_text = " ".join(
                text for _, text, _ in results
            )

            return extracted_text.strip()

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}"
        )