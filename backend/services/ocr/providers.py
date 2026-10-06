import os
import base64
import cv2
import numpy as np
import requests
from services.ocr.base_ocr import BaseOCR

class EasyOCRProvider(BaseOCR):
    def __init__(self):
        import easyocr
        self.reader = easyocr.Reader(["en"], gpu=False)

    def extract_text(self, img_array: np.ndarray) -> str:
        results = self.reader.readtext(img_array)
        return " ".join(t for _, t, _ in results).strip()

class TesseractProvider(BaseOCR):
    def __init__(self):
        import pytesseract
        self.pytesseract = pytesseract

    def extract_text(self, img_array: np.ndarray) -> str:
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        return self.pytesseract.image_to_string(gray).strip()

class GPT4oVisionProvider(BaseOCR):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for GPT4oVisionProvider")

    def extract_text(self, img_array: np.ndarray) -> str:
        _, buffer = cv2.imencode('.jpg', img_array)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this image exactly as written. If there are tables, format them properly. Return ONLY the extracted text."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()

class AzureOCRProvider(BaseOCR):
    def __init__(self):
        self.api_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        self.endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        if not self.api_key or not self.endpoint:
            raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_KEY and ENDPOINT are required")

    def extract_text(self, img_array: np.ndarray) -> str:
        # Placeholder for Azure Doc Intelligence implementation
        # Uses Document Intelligence REST API
        pass
