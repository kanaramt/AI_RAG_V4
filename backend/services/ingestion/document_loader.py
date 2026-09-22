from pathlib import Path

from services.ingestion.base_loader import BaseLoader


class DocumentLoader(BaseLoader):
    """
    Loads supported document types.
    """

    def load(
        self,
        file_path: str,
    ) -> str:

        extension = Path(file_path).suffix.lower()

        if extension == ".txt":

            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as file:

                return file.read()

        raise ValueError(
            f"Unsupported file type: {extension}"
        )
