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
    async def ingest_file(
        file: Any,
        memory,
        embedding_model: str | None = None,
        embedding_api_key: str | None = None,
    ):
        """
        Ingest a file uploaded from the UI.
        """
        return await IngestionService.ingest_upload(
            file,
            memory,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )

    @staticmethod
    async def ingest_local_file(
        file_path: Path,
        memory,
        embedding_model: str | None = None,
        embedding_api_key: str | None = None,
    ):
        """
        Ingest a file from the local knowledge base.
        """
        return await IngestionService.ingest_local_file(
            file_path,
            memory,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )

    @staticmethod
    async def ingest_url(
        url: str,
        memory,
        embedding_model: str | None = None,
        embedding_api_key: str | None = None,
    ):
        """
        Ingest a web page.
        """
        return await IngestionService.ingest_url(
            url,
            memory,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )

    @staticmethod
    async def ingest_pasted_content(
        title: str,
        content: str,
        memory,
        embedding_model: str | None = None,
        embedding_api_key: str | None = None,
    ):
        """
        Ingest pasted text.
        """
        return await IngestionService.ingest_pasted_content(
            title,
            content,
            memory,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
        )