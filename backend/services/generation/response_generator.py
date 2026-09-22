from services.generation.base_generator import BaseGenerator
from services.generation.prompt_builder import PromptBuilder
from services.llm.llm_factory import LLMFactory


class ResponseGenerator(BaseGenerator):
    """
    Generates grounded responses using the configured LLM.
    """

    def __init__(self):

        self.prompt_builder = PromptBuilder()
        self.llm = LLMFactory.create()

    def generate(
        self,
        query: str,
        context: str,
    ) -> str:

        prompt = self.prompt_builder.build(
            query=query,
            context=context,
        )

        return self.llm.invoke(prompt)
