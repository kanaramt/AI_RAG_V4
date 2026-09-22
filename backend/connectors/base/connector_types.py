"""
===========================================================
Connector Types

Purpose
-------
Defines all supported connector types in one place.

Using an Enum prevents hardcoded strings throughout
the platform.

Example

Instead of:

    "sqlserver"

Use:

    ConnectorType.SQL_SERVER
===========================================================
"""

from enum import Enum


class ConnectorType(str, Enum):
    """
    Supported connector types.
    """

    LOCAL = "local"

    SQLITE = "sqlite"
    SQL_SERVER = "sqlserver"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

    SHAREPOINT = "sharepoint"
    ONEDRIVE = "onedrive"

    GOOGLE_DRIVE = "google_drive"
    GOOGLE_DOCS = "google_docs"
    GOOGLE_SHEETS = "google_sheets"

    WEB_URL = "web_url"
    REST_API = "rest_api"
    SITEMAP = "sitemap"
