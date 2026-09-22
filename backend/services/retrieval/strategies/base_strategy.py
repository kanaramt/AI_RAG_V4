from abc import ABC, abstractmethod

from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse


class BaseRetrievalStrategy(ABC):
    """
    Base class for all retrieval strategies.
    """

    @abstractmethod
    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResponse, str]:
        """
        Execute a retrieval strategy.

        Returns:
            (RetrievalResponse, Context)
        """
        pass
