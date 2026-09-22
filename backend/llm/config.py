from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """
    Common configuration shared by all LLM providers.
    """

    provider: str = Field(default="ollama")

    model: str = Field(default="llama3:8b")

    api_key: str | None = None

    base_url: str | None = None

    temperature: float = 0.2

    max_tokens: int = 4096

    timeout: int = 120

    stream: bool = True
