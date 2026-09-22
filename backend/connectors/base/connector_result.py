"""
===========================================================
Connector Result

Purpose
-------
Every connector should return data in the same format.

Whether the connector is:

- Local Files
- SQL Server
- SharePoint
- Google Drive
- REST API

the output should always follow this model.

This keeps the rest of the platform independent from
where the data came from.
===========================================================
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectorResult:
    """
    Standard result returned by every connector.
    """

    # Was the connector operation successful?
    success: bool

    # Human-readable message.
    message: str = ""

    # Raw data returned from the connector.
    data: Any = None

    # Metadata describing the source.
    metadata: dict = field(default_factory=dict)

    # Number of discovered items.
    total_items: int = 0

    # Optional error information.
    error: str | None = None
