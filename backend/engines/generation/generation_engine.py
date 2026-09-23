"""
Enterprise Generation Engine

Orchestrates LLM response generation.
"""

from typing import Any

from llm.factory import LLMFactory


class GenerationEngine:
    """
    Enterprise Generation Engine.
    """

    async def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.2,
    ) -> str:
        """
        Generate a response using the selected LLM.
        """

        print("=" * 80)
        print(f"[GENERATION DEBUG] Requested model = {model}")
        print("=" * 80)

        provider = LLMFactory.get_llm_by_model(
            model_name=model,
            temperature=temperature,
        )

        print(f"[DEBUG MODEL RECEIVED] {model}")
        print(f"[DEBUG PROVIDER] {provider.__class__.__name__}")

        llm = provider
        print(f"[GENERATION DEBUG] Provider = {type(llm).__name__}")
        print(f"[GENERATION ENGINE] Calling model: {model}")

        response = await llm.chat(messages)
        print(f"[GENERATION ENGINE] Response received. Length={len(response)}")

        print(f"[GENERATION END] model={model}")

        return response
