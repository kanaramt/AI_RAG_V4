"""
===========================================================
Connector Registry

Purpose
-------
The Connector Registry maintains a central list of all
available connectors in the platform.

Instead of hardcoding connectors throughout the application,
every connector registers itself here.

Benefits
--------
- One central place to manage connectors
- Easy to add new connectors
- No changes required in business logic
- Supports plug-in architecture
===========================================================
"""

from typing import Dict

from connectors.base.base_connector import BaseConnector
from connectors.base.connector_types import ConnectorType


class ConnectorRegistry:
    """
    Central registry for all platform connectors.
    """

    def __init__(self):
        # Stores all registered connectors.
        self._connectors: Dict[ConnectorType, BaseConnector] = {}

    def register(
        self,
        connector_type: ConnectorType,
        connector: BaseConnector,
    ) -> None:
        """
        Register a connector.

        Example
        -------
        ConnectorType.LOCAL
            -> LocalFileConnector()
        """

        self._connectors[connector_type] = connector

    def get(
        self,
        connector_type: ConnectorType,
    ) -> BaseConnector:
        """
        Return a registered connector.

        Raises
        ------
        ValueError
            If the connector is not registered.
        """

        if connector_type not in self._connectors:
            raise ValueError(
                f"Connector '{connector_type}' is not registered."
            )

        return self._connectors[connector_type]

    def list_connectors(self) -> list[ConnectorType]:
        """
        Return all registered connector types.
        """

        return list(self._connectors.keys())

    def is_registered(
        self,
        connector_type: ConnectorType,
    ) -> bool:
        """
        Check whether a connector is registered.
        """

        return connector_type in self._connectors


# ---------------------------------------------------------
# Global Connector Registry
#
# The platform uses one shared registry instance.
# Every connector registers itself here during startup.
# ---------------------------------------------------------

connector_registry = ConnectorRegistry()
