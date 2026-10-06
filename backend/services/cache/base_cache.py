from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseCache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
