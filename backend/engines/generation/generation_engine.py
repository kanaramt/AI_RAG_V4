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

        print(f"[GENERATION START] model={model}")
        
        llm = LLMFactory.get_llm_by_model(
            model_name=model,
            temperature=temperature,
        )

        print(f"[GENERATION ENGINE] Calling model: {model}")

        response = await llm.chat(messages)
        print(f"[GENERATION ENGINE] Response received. Length={len(response)}")

        print(f"[GENERATION END] model={model}")

        return response
