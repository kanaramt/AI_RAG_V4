from llm.providers.claude import ClaudeProvider
from llm.providers.gemini import GeminiProvider
from llm.providers.grok import GrokProvider
from llm.providers.groq import GroqProvider
from llm.providers.ollama import OllamaProvider
from llm.providers.openai import OpenAIProvider


LLM_PROVIDER_REGISTRY = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "claude": ClaudeProvider,
    "grok": GrokProvider,
    "groq": GroqProvider,
}
