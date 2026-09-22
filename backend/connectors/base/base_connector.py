"""
===========================================================
Base Connector

Purpose
-------
This is the parent class for every connector in the platform.

Every connector (Local Files, SQL Server, SharePoint,
Google Drive, Web URLs, etc.) must inherit from this class.

Why?
----
Using one common interface keeps every connector consistent,
easy to maintain, and easy to extend.

Future connectors only need to implement these methods
instead of creating their own structure.
===========================================================
"""

from abc import ABC, abstractmethod


class BaseConnector(ABC):
    """
    Base class for all connectors.

    Every connector must implement these methods.
    """

    @property
    @abstractmethod
    def connector_name(self) -> str:
        """
        Returns the connector name.

        Example:
            Local Files
            SQL Server
            SharePoint
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Verify that the connector can connect successfully.

        Returns
        -------
        True
            Connection successful

        False
            Connection failed
        """
        pass

    @abstractmethod
    def discover(self):
        """
        Discover available data.

        Examples
        --------
        Local Files
            Returns all supported files.

        SQL Server
            Returns databases/tables.

        SharePoint
            Returns folders/documents.
        """
        pass

    @abstractmethod
    def extract(self):
        """
        Extract raw data from the source.

        This method DOES NOT:

        - chunk
        - embed
        - store vectors

        It only extracts raw data.
        """
        pass

    @abstractmethod
    def metadata(self):
        """
        Return metadata describing the source.

        Examples

        filename
        owner
        source
        modified_date
        size
        """
        pass
