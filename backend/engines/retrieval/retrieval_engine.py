"""
Enterprise Retrieval Engine

Orchestrates retrieval workflows.
"""

from schemas.retrieval.retrieval_request import RetrievalRequest
from services.retrieval.retrieval_service import RetrievalService


class RetrievalEngine:
    """
    Enterprise Retrieval Engine.
    """

    def __init__(self):
        self.retrieval_service = RetrievalService()

    async def retrieve(
        self,
        request: RetrievalRequest,
    ):
        """
        Execute the complete retrieval pipeline.
        """

        return await self.retrieval_service.retrieve(request)
