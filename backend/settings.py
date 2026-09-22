from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    APP_NAME: str = "AI RAG"
    APP_VERSION: str = "2.0.0"

    DEBUG: bool = True
    SYSTEM_PROMPT: str = "You are AI RAG playground, developed by AI Engineers. You are a premium AI assistant designed to read, retrieve, and explain code, documents, snapshots, and web links for users. Answer clearly in markdown."

    # Database
    DATABASE_URL: str = "sqlite:///./enterprise_rag.db"

    # LLM Configuration
    DEFAULT_PROVIDER: str = "groq"
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # Retrieval
    VECTOR_STORE: str = "hybrid"
    RETRIEVAL_STRATEGY: str = "multi_query"
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # Local Models
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    CHAT_MODEL: str = "llama3:latest"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # Chunking
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 400

    # Retrieval Thresholds
    RETRIEVAL_MIN_SCORE: float = 0.75
    MIN_REQUIRED_CHUNKS: int = 2

    # Qdrant Configuration
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    @property
    def BACKEND_DIR(self) -> Path:
        return BACKEND_DIR

    @property
    def PROJECT_ROOT(self) -> Path:
        return PROJECT_ROOT


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
print("DATABASE_URL =", settings.DATABASE_URL)
