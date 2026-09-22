"""
Enterprise Document Intelligence Engine

Orchestrates all document processing.
"""

from fastapi import UploadFile

from services.document_intelligence import DocumentIntelligence


class DocumentIntelligenceEngine:
    """
    Orchestrates document processing.
    """

    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        """
        Extract text from any supported document.
        """
        return await DocumentIntelligence.extract_text(file)
