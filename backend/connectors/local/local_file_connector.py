"""
===========================================================
Local File Connector

Purpose
-------
This connector discovers files stored on the local machine.

It DOES NOT:
    - Read document contents
    - Chunk documents
    - Generate embeddings
    - Store vectors

Those responsibilities belong to other engines.

This connector only discovers files and returns
their information.
===========================================================
"""

from pathlib import Path

from connectors.base.base_connector import BaseConnector
from connectors.base.connector_result import ConnectorResult


class LocalFileConnector(BaseConnector):
    """
    Connector for local folders.
    """

    def __init__(self, root_directory: Path):
        """
        Parameters
        ----------
        root_directory

        Folder that will be scanned.
        """

        self.root_directory = root_directory

    @property
    def connector_name(self) -> str:
        """
        Human readable connector name.
        """

        return "Local Files"

    def test_connection(self) -> bool:
        """
        Local folders don't require authentication.

        The connection is valid if the folder exists.
        """

        return self.root_directory.exists()

    def discover(self) -> ConnectorResult:
        """
        Discover every file inside the configured folder.

        No filtering is performed here.

        Filtering belongs to higher layers.
        """

        if not self.test_connection():

            return ConnectorResult(
                success=False,
                message="Directory not found.",
            )

        files = []

        for item in self.root_directory.rglob("*"):

            if item.is_file():
                files.append(item)

        return ConnectorResult(
            success=True,
            message="Files discovered successfully.",
            data=files,
            total_items=len(files),
        )

    def extract(self):
        """
        Extraction is handled later by the
        Document Intelligence Engine.
        """

        raise NotImplementedError(
            "Extraction is handled by the Document Intelligence Engine."
        )

    def metadata(self):
        """
        Return basic connector metadata.
        """

        return {
            "connector": self.connector_name,
            "root_directory": str(self.root_directory),
        }
