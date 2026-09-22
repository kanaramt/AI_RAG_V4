import re


class SentenceSplitter:
    """
    Production-ready sentence splitter.

    Preserves sentence boundaries while handling
    common punctuation and whitespace.
    """

    def split(
        self,
        text: str,
    ) -> list[str]:

        if not text or not text.strip():
            return []

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Split after sentence-ending punctuation
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]
