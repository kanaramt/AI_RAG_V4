"""
Enterprise Ingestion Engine

This engine orchestrates the complete ingestion workflow.
It does not implement business logic itself. Instead, it
coordinates existing services.
"""

from pathlib import Path
from typing import Any

from services.ingestion_service import IngestionService


class IngestionEngine:
    """
    Orchestrates ingestion workflows.
    """

    @staticmethod
    async def ingest_file(file: Any, memory):
        """
        Ingest a file uploaded from the UI.
        """
        return await IngestionService.ingest_upload(file, memory)

    @staticmethod
    async def ingest_local_file(file_path: Path, memory):
        """
        Ingest a file from the local knowledge base.
        """
        return await IngestionService.ingest_local_file(file_path, memory)

    @staticmethod
    async def ingest_url(url: str, memory):
        """
        Ingest a web page.
        """
        return await IngestionService.ingest_url(url, memory)

    @staticmethod
    async def ingest_pasted_content(title: str, content: str, memory):
        """
        Ingest pasted text.
        """
        return await IngestionService.ingest_pasted_content(
            title,
            content,
            memory,
        )
