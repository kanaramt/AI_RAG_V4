from llm.factory import LLMFactory
from settings import settings


class QueryRewriter:
    """
    Enterprise Query Rewriter.

    Responsibilities
    ----------------
    • Rewrite user queries
    • Generate multiple semantic search queries
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
                print(f"[QueryRewriter] LLM initialization warning: {clean_err}")
                self._llm = None
        return self._llm

    async def rewrite(self, query: str) -> str:
        """
        Rewrite a user query for better semantic retrieval.
        """
        if not self.llm:
            return query

        prompt = f"""
Rewrite the following query for semantic document retrieval.

Rules:
- Preserve the original meaning.
- Expand abbreviations if useful.
- Remove unnecessary words.
- Return ONLY the rewritten query.

Query:
{query}
"""

        try:
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}]
            )
            return response.strip() if response else query

        except Exception as e:
            print(f"[QueryRewriter] Rewrite failed: {e}")
            return query


    async def generate_search_queries(
        self,
        query: str,
    ) -> list[str]:
        """
        Generate multiple semantic search queries.
        """
        if not self.llm:
            return [query]

        prompt = f"""
Generate 5 different search queries for retrieving documents.

Requirements:
- Same intent
- Different wording
- Different keywords
- One query per line
- No numbering
- No explanations

User Query:
{query}
"""

        try:

            response = await self.llm.chat(
                [{"role": "user", "content": prompt}]
            )

            queries = [
                line.strip()
                for line in response.splitlines()
                if line.strip()
            ] if response else []

            queries.insert(0, query)

            # Remove duplicates while preserving order
            unique_queries = list(dict.fromkeys(queries))

            return unique_queries

        except Exception as e:
            clean_err = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"[QueryRewriter] Multi-query failed: {clean_err}")
            return [query]
