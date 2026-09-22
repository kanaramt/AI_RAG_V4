import threading
from functools import lru_cache
from sqlalchemy.orm import Session

from database.session import get_db

from settings import settings
from memory.memory_service import MemoryService
from engines.retrieval.retrieval_engine import RetrievalEngine

_memory_service = None
_retrieval_engine = None
_dep_lock = threading.Lock()


@lru_cache
def get_settings():
    """
    FastAPI dependency for application settings.
    """
    return settings


def get_memory() -> MemoryService:
    """
    Get or create a singleton MemoryService safely across threads.
    """
    global _memory_service
    if _memory_service is None:
        with _dep_lock:
            if _memory_service is None:
                _memory_service = MemoryService()
    return _memory_service


def get_retrieval_service() -> RetrievalEngine:
    """
    Get or create a singleton RetrievalEngine safely across threads.
    """
    global _retrieval_engine

    if _retrieval_engine is None:
        with _dep_lock:
            if _retrieval_engine is None:
                _retrieval_engine = RetrievalEngine()

    return _retrieval_engine

def get_database() -> Session:
    """
    FastAPI dependency wrapper for SQLAlchemy Session.
    """
    yield from get_db()
