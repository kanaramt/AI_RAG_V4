from abc import ABC, abstractmethod
from typing import List
from schemas.retrieval.retrieved_document import RetrievedDocument

class BaseReranker(ABC):
    """
    Abstract base class for all Rerankers.
    """
    @abstractmethod
    def rerank(self, query: str, documents: List[RetrievedDocument], top_k: int = 3) -> List[RetrievedDocument]:
        pass
