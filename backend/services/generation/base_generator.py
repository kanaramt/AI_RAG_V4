from abc import ABC, abstractmethod


class BaseGenerator(ABC):
    """
    Base interface for all response generators.
    """

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
    ) -> str:
        """
        Generate an answer from the given query and context.
        """
        pass
