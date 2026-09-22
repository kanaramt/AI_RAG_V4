import re


class TextCleaner:
    """
    Cleans extracted document text.
    """

    def clean(
        self,
        text: str,
    ) -> str:

        text = text.replace("\r", "\n")

        text = re.sub(
            r"\n+",
            "\n",
            text,
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        return text.strip()
