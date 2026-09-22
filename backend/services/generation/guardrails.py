class Guardrails:
    """
    Validates generated responses.
    """

    def validate(
        self,
        response: str,
    ) -> str:

        if not response:
            return "No response generated."

        if not response.strip():
            return "No response generated."

        return response
