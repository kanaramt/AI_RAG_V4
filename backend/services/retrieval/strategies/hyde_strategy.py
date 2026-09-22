from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse

from services.retrieval.hyde_generator import HyDEGenerator
from services.retrieval.strategies.hybrid_strategy import HybridStrategy


class HyDEStrategy:
    """
    HyDE Retrieval Strategy.

    Workflow

    User Query
         ↓
    Generate Hypothetical Answer
         ↓
    Hybrid Retrieval
         ↓
    Return Results
    """

    def __init__(self):

        self.hyde = HyDEGenerator()

        self.hybrid = HybridStrategy()

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResponse, str]:

        hypothetical_document = await self.hyde.generate(
            request.query
        )

        hyde_request = request.model_copy(
            update={
                "query": hypothetical_document
            }
        )

        return await self.hybrid.retrieve(
            hyde_request
        )
