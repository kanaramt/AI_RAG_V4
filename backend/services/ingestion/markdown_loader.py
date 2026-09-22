from services.ingestion.base_loader import BaseLoader


class MarkdownLoader(BaseLoader):
    """
    Loader for Markdown documents.
    """

    def load(self) -> str:
        """
        Read the markdown file and return its contents.
        """

        if not self.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        return self.file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
