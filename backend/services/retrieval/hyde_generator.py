from llm.factory import LLMFactory
from settings import settings


class HyDEGenerator:
    """
    HyDE (Hypothetical Document Embeddings)

    Generates an ideal answer for a query.
    That answer is then used for retrieval.
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
                print(f"[HyDE] LLM initialization warning: {clean_err}")
                self._llm = None
        return self._llm

    async def generate(
        self,
        query: str,
    ) -> str:
        if not self.llm:
            return query


        prompt = f"""
You are generating a hypothetical document.

Write a detailed paragraph that perfectly answers the question.

Do NOT mention that this is hypothetical.

Question:

{query}
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

            print(f"[HyDE] {e}")

            return query
