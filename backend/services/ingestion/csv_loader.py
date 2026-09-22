import pandas as pd

from services.ingestion.base_loader import BaseLoader


class CSVLoader(BaseLoader):
    """
    Loader for CSV documents.
    """

    def load(self) -> str:
        """
        Read a CSV file and convert it into readable text.
        """

        if not self.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        dataframe = pd.read_csv(self.file_path)

        return dataframe.to_string(index=False)
