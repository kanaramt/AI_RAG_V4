from services.retrieval.strategies.hybrid_strategy import HybridStrategy
from services.retrieval.strategies.multi_query_strategy import MultiQueryStrategy
from services.retrieval.strategies.hyde_strategy import HyDEStrategy


class RetrievalStrategyFactory:
    """
    Factory responsible for creating retrieval strategies.

    Available Strategies
    --------------------
    - hybrid
    - multi_query
    - hyde
    """

    _strategies = {
        "hybrid": HybridStrategy,
        "multi_query": MultiQueryStrategy,
        "hyde": HyDEStrategy,
    }

    @classmethod
    def create(
        cls,
        strategy_name: str = "multi_query",
    ):

        strategy = cls._strategies.get(
            strategy_name.lower()
        )

        if strategy is None:

            available = ", ".join(
                cls._strategies.keys()
            )

            raise ValueError(
                f"Unknown retrieval strategy '{strategy_name}'. "
                f"Available: {available}"
            )

        return strategy()
