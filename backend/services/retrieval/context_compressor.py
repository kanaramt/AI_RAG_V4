from llm.factory import LLMFactory
from settings import settings


class ContextCompressor:
    """
    Compresses retrieved context before sending it to the LLM.

    Responsibilities
    ----------------
    • Remove irrelevant information
    • Preserve important facts
    • Reduce token usage
    """

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            try:
                self._llm = LLMFactory.get_llm_by_model(settings.LLM_MODEL)
            except Exception as e:
                clean_err = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"[ContextCompressor] LLM initialization warning: {clean_err}")
                self._llm = None
        return self._llm

    async def compress(
        self,
        query: str,
        context: str,
    ) -> str:
        if not self.llm:
            return context


        prompt = f"""
You are an expert retrieval context compressor.

User Question:
{query}

Retrieved Context:
{context}

Instructions:
- Keep only information useful for answering the question.
- Remove duplicate information.
- Remove irrelevant paragraphs.
- Preserve important facts.
- Do NOT answer the question.
- Return only the compressed context.
"""

        try:

            response = await self.llm.chat(
                [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            )

            return response.strip()

        except Exception as e:

            print(f"[ContextCompressor] {e}")

            return context
