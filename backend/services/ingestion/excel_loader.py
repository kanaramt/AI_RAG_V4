import pandas as pd

from services.ingestion.base_loader import BaseLoader


class ExcelLoader(BaseLoader):
    """
    Loader for Microsoft Excel documents.
    """

    def load(self) -> str:
        """
        Read all sheets from an Excel workbook and convert them into readable text.
        """

        if not self.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        workbook = pd.read_excel(
            self.file_path,
            sheet_name=None,
        )

        sheets = []

        for sheet_name, dataframe in workbook.items():
            sheets.append(f"Sheet: {sheet_name}")
            sheets.append(dataframe.to_string(index=False))
            sheets.append("")

        return "\n".join(sheets)
