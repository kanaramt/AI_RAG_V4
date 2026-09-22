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

        llm = LLMFactory.get_llm_by_model(
            model_name=model,
            temperature=temperature,
        )

        return await llm.chat(messages)
