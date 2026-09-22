from anthropic.types.beta import beta_managed_agents_agent_tool_config_params
from anthropic.types.beta import beta_managed_agents_agent_tool_config_params
from anthropic.types.beta import beta_managed_agents_agent_tool_config_params
from anthropic.types.beta import beta_managed_agents_agent_tool_config_params
from anthropic.types.beta import beta_managed_agents_agent_tool_config_params
from anthropic.types.beta import beta_managed_agents_agent_tool_config_params
from schemas.retrieval.retrieval_request import RetrievalRequest
from schemas.retrieval.retrieval_response import RetrievalResponse
from settings import settings

from services.retrieval.strategies.factory import RetrievalStrategyFactory
from services.retrieval.strategies.multi_query_strategy import MultiQueryStrategy


class RetrievalService:
    """
    Enterprise Retrieval Service.

    Acts as the entry point for all retrieval requests and delegates
    execution to the configured retrieval strategy.
    """

    def __init__(self):

        # Create retrieval strategy using the factory.
        # Available:
        #   hybrid
        #   multi_query
        #   hyde
        self.strategy = RetrievalStrategyFactory.create(
        settings.RETRIEVAL_STRATEGY
    )

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResponse, str]:

        return await self.strategy.retrieve(request)
