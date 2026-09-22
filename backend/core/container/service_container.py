"""
===========================================================
Service Container

Purpose
-------
The Service Container is responsible for creating and
providing shared services used throughout the platform.

Why?

Instead of every Engine creating its own service objects,
all Engines request services from this container.

Benefits
--------
- Single place to manage services
- Easy testing and mocking
- Reusable shared instances
- Cleaner Engine code
- Easier dependency management
===========================================================
"""

from typing import Any


class ServiceContainer:
    """
    Central registry for platform services.
    """

    def __init__(self):
        # Stores service instances.
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        """
        Register a service instance.

        Example
        -------
        register("embedding_service", EmbeddingService())
        """

        self._services[name] = service

    def get(self, name: str) -> Any:
        """
        Retrieve a registered service.

        Raises
        ------
        ValueError
            If the service is not registered.
        """

        if name not in self._services:
            raise ValueError(
                f"Service '{name}' is not registered."
            )

        return self._services[name]

    def is_registered(self, name: str) -> bool:
        """
        Check whether a service has been registered.
        """

        return name in self._services


# ---------------------------------------------------------
# Global Service Container
#
# One shared container for the entire platform.
# ---------------------------------------------------------

service_container = ServiceContainer()
