import os
from services.ocr.base_ocr import BaseOCR
from services.ocr.providers import EasyOCRProvider, TesseractProvider, GPT4oVisionProvider, AzureOCRProvider

class OCRFactory:
    @staticmethod
    def create() -> BaseOCR:
        provider = os.getenv("ACTIVE_OCR_PROVIDER", "tesseract").lower()
        
        if provider == "gpt4o":
            return GPT4oVisionProvider()
        elif provider == "azure":
            return AzureOCRProvider()
        elif provider == "tesseract":
            return TesseractProvider()
        else:
            return EasyOCRProvider()
