from llm.config import LLMConfig
from llm.registry import LLM_PROVIDER_REGISTRY
from llm.providers.base import BaseLLMProvider


def _get_env_key(key_name: str, fallback_key: str = None) -> str:
    """
    Robust key resolver: checks os.environ, and if missing, reloads directly from .env file.
    """
    import os
    from pathlib import Path
    from dotenv import dotenv_values

    val = os.getenv(key_name) or (os.getenv(fallback_key) if fallback_key else None)
    if val and val.strip():
        return val.strip()

    try:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        if env_file.exists():
            env_dict = dotenv_values(env_file)
            val = env_dict.get(key_name) or (env_dict.get(fallback_key) if fallback_key else None)
            if val and val.strip():
                os.environ[key_name] = val.strip()
                if fallback_key:
                    os.environ[fallback_key] = val.strip()
                return val.strip()
    except Exception:
        pass
    return ""

MODEL_PROVIDER_MAP = {
    # ============================================================
    # OPENAI
    # ============================================================
    "gpt-5.5": "openai",
    "gpt-5.4": "openai",
    "gpt-5.4-mini": "openai",
    "gpt-5.4-nano": "openai",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4.1": "openai",
    "gpt-4.1-mini": "openai",

    # ============================================================
    # ANTHROPIC CLAUDE
    # ============================================================
    "claude-opus-5": "claude",
    "claude-opus-4-8": "claude",
    "claude-opus-4-7": "claude",
    "claude-opus-4-6": "claude",
    "claude-sonnet-5": "claude",
    "claude-sonnet-4-6": "claude",
    "claude-sonnet-4-5-20250929": "claude",
    "claude-haiku-4-5-20251001": "claude",

    # ============================================================
    # GOOGLE GEMINI
    # ============================================================
    "gemini-3.8-flash": "gemini",
    "gemini-3.7-flash": "gemini",
    "gemini-3.6-flash": "gemini",
    "gemini-3.5-flash": "gemini",
    "gemini-3.5-flash-lite": "gemini",
    "gemini-3.1-flash-lite": "gemini",

    # ============================================================
    # XAI GROK
    # ============================================================
    "grok-4.7": "grok",
    "grok-4.6": "grok",
    "grok-4.5": "grok",

    # ============================================================
    # GROQ CLOUD
    # ============================================================
    "openai/gpt-oss-120b": "groq",
    "openai/gpt-oss-20b": "groq",

    # ============================================================
    # OLLAMA LOCAL
    # ============================================================
    "llama3": "ollama",
    "llama3:8b": "ollama",
    "llama3:latest": "ollama",
    "llama3.1": "ollama",
    "llama3.1:latest": "ollama",
    "llama3.2": "ollama",
    "llama3.2:latest": "ollama",
    "mistral": "ollama",
    "mistral:7b": "ollama",
    "mistral:latest": "ollama",
    "phi3": "ollama",
    "phi3:3.8b": "ollama",
    "phi3:latest": "ollama",
    "phi3.5": "ollama",
    "deepseek-r1": "ollama",
    "gemma2": "ollama",
    "qwen2.5": "ollama",
}

class LLMFactory:
    """
    Factory responsible for creating
    the appropriate LLM provider.
    """

    @staticmethod
    def create(config: LLMConfig) -> BaseLLMProvider:

        provider_name = config.provider.lower()

        provider_class = LLM_PROVIDER_REGISTRY.get(provider_name)

        if provider_class is None:
            available = ", ".join(LLM_PROVIDER_REGISTRY.keys())

            raise ValueError(
                f"Unsupported provider '{provider_name}'. "
                f"Available providers: {available}"
            )

        return provider_class(config)

    @staticmethod
    def get_llm_by_model(model_name: str, temperature: float = 0.2) -> BaseLLMProvider:
        """
        Dynamically construct the LLM provider based on the model name.
        """
        import os
        from settings import settings

        model_name_lower = model_name.lower()
        print("=" * 80)
        print("[LLM FACTORY DEBUG]")
        print(f"Incoming model_name = {model_name}")
        print(f"Incoming model_name_lower = {model_name_lower}")
        print("=" * 80)
        
        provider = MODEL_PROVIDER_MAP.get(model_name_lower)

        if provider is None:
            raise ValueError(
                f"Unsupported model '{model_name}'. "
                "The model is not registered in MODEL_PROVIDER_MAP."
            )

        # Preserve the exact model selected by the user.
        model = model_name

        if provider == "openai":
            api_key = _get_env_key("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "⚠️ OpenAI API Key is missing. "
                    "Please add your OPENAI_API_KEY in Settings -> API Keys & Cloud LLMs."
                )
            base_url = None

        elif provider == "claude":
            api_key = _get_env_key("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "⚠️ Anthropic Claude API Key is missing. "
                    "Please add your ANTHROPIC_API_KEY in Settings -> API Keys & Cloud LLMs."
                )
            base_url = None

        elif provider == "gemini":
            api_key = _get_env_key("GEMINI_API_KEY", "GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "⚠️ Google Gemini API Key is missing. "
                    "Please add your GEMINI_API_KEY in Settings -> API Keys & Cloud LLMs."
                )
            base_url = None

        elif provider == "grok":
            api_key = _get_env_key("GROK_API_KEY", "XAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "⚠️ xAI Grok API Key is missing. "
                    "Please add your GROK_API_KEY in Settings -> API Keys & Cloud LLMs."
                )
            base_url = "https://api.x.ai/v1"

        elif provider == "groq":
            api_key = _get_env_key("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "⚠️ Groq API Key is missing. "
                    "Please add your GROQ_API_KEY in Settings -> API Keys & Cloud LLMs."
                )
            base_url = "https://api.groq.com/openai/v1"

        elif provider == "ollama":
            api_key = None
            base_url = settings.OLLAMA_BASE_URL

            # Frontend uses friendly aliases for these local models.
            if model_name_lower == "llama3":
                model = "llama3:latest"
            elif model_name_lower == "llama3.2":
                model = "llama3.2:latest"
            elif model_name_lower == "mistral":
                model = "mistral:latest"
            elif model_name_lower == "phi3":
                model = "phi3:latest"

        config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature
        )

        print("[LLM FACTORY FINAL]")
        print(f"Provider = {provider}")
        print(f"Model = {model}")
        print(f"Base URL = {base_url}")
        print(f"API Key Present = {bool(api_key)}")
        
        return LLMFactory.create(config)