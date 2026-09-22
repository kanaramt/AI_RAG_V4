from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse

from services.retrieval.query_rewriter import QueryRewriter
from services.retrieval.strategies.hybrid_strategy import HybridStrategy


class MultiQueryStrategy:
    """
    Enterprise Multi-Query Retrieval Strategy.

    Workflow

    User Query
         ↓
    Generate Multiple Queries
         ↓
    Hybrid Retrieval (for each query)
         ↓
    Merge Results
         ↓
    Remove Duplicates
         ↓
    Build Context
    """

    def __init__(self):

        self.query_rewriter = QueryRewriter()

        self.hybrid_strategy = HybridStrategy()

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResponse, str]:

        search_queries = await self.query_rewriter.generate_search_queries(
            request.query
        )

        all_documents = []

        total_time = 0

        context = ""

        for query in search_queries:

            new_request = request.model_copy(
                update={"query": query}
            )

            response, current_context = await self.hybrid_strategy.retrieve(
                new_request
            )

            total_time += response.retrieval_time_ms

            context += "\n" + current_context

            all_documents.extend(response.documents)

        # Remove duplicate chunks
        unique_documents = []

        seen = set()

        for document in all_documents:
            key = getattr(document, "id", None) or getattr(document, "text", "")
            if key not in seen:
                seen.add(key)
                unique_documents.append(document)


        final_response = RetrievalResponse(

            documents=unique_documents,

            total_documents=len(unique_documents),

            retrieval_time_ms=total_time,

            retriever_name="MultiQueryStrategy",
        )

        return final_response, context
