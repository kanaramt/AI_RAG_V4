from pathlib import Path
from fastapi import HTTPException, UploadFile


class DocumentExtractor:
    """
    Extracts text from uploaded and local documents.

    Supports:
    - TXT
    - PDF (via pypdf)
    - DOCX (via python-docx)
    - CSV (via csv standard library)
    - XLSX / XLS (via openpyxl and pandas fallback)
    - PPTX (via python-pptx)
    - JSON
    """

    @classmethod
    async def extract_text(cls, file: UploadFile) -> str:
        extension = Path(file.filename).suffix.lower()

        if extension == ".txt":
            return await cls._extract_txt(file)

        elif extension == ".pdf":
            return await cls._extract_pdf(file)

        elif extension in {".docx", ".doc"}:
            return await cls._extract_docx(file)

        elif extension in {".xlsx", ".xls"}:
            return await cls._extract_xlsx(file)

        elif extension in {".pptx", ".ppt"}:
            return await cls._extract_pptx(file)

        elif extension == ".csv":
            return await cls._extract_csv(file)

        elif extension == ".json":
            return await cls._extract_json(file)

        raise HTTPException(
            status_code=400,
            detail=f"No extractor available for '{extension}' files."
        )

    @staticmethod
    async def _extract_xlsx(file: UploadFile) -> str:
        """
        Extract structured tabular text from an Excel file (.xlsx, .xls) using openpyxl & pandas.
        """
        import io
        contents = await file.read()
        await file.seek(0)

        # Primary extraction using openpyxl
        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True, read_only=True)
            sheet_texts = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                rows_text = []
                for row in ws.iter_rows(values_only=True):
                    cells = [str(cell).strip() if cell is not None else "" for cell in row]
                    # Only include non-empty rows
                    if any(cells):
                        rows_text.append(" | ".join(cells))
                if rows_text:
                    sheet_texts.append(f"=== Sheet: {sheet_name} ===\n" + "\n".join(rows_text))
            wb.close()
            if sheet_texts:
                return "\n\n".join(sheet_texts)
        except Exception:
            pass

        # Fallback extraction using pandas
        try:
            import pandas as pd
            excel_file = pd.ExcelFile(io.BytesIO(contents))
            sheet_texts = []
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                if not df.empty:
                    sheet_texts.append(f"=== Sheet: {sheet_name} ===\n" + df.to_string(index=False))
            if sheet_texts:
                return "\n\n".join(sheet_texts)
        except Exception as e2:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from Excel file: {e2}")

        return ""

    @staticmethod
    async def _extract_pptx(file: UploadFile) -> str:
        """
        Extract slide text, headings, speaker notes, and tables from PowerPoint (.pptx).
        """
        import io
        try:
            from pptx import Presentation
        except ImportError:
            raise HTTPException(status_code=500, detail="python-pptx library is not installed.")

        contents = await file.read()
        await file.seek(0)

        try:
            prs = Presentation(io.BytesIO(contents))
            slides_text = []

            for idx, slide in enumerate(prs.slides, start=1):
                slide_parts = [f"--- Slide {idx} ---"]

                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            text = "".join(run.text for run in paragraph.runs).strip()
                            if not text and paragraph.text:
                                text = paragraph.text.strip()
                            if text:
                                slide_parts.append(text)
                    elif shape.has_table:
                        table = shape.table
                        for row in table.rows:
                            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if row_cells:
                                slide_parts.append(" | ".join(row_cells))

                if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                    notes_text = slide.notes_slide.notes_text_frame.text.strip()
                    if notes_text:
                        slide_parts.append(f"[Speaker Notes: {notes_text}]")

                if len(slide_parts) > 1:
                    slides_text.append("\n".join(slide_parts))

            return "\n\n".join(slides_text)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from PowerPoint file: {e}")

    @staticmethod
    async def _extract_docx(file: UploadFile) -> str:
        """
        Extract paragraphs and table content from Word document (.docx).
        """
        import io
        try:
            import docx
        except ImportError:
            raise HTTPException(status_code=500, detail="python-docx library is not installed.")

        contents = await file.read()
        await file.seek(0)

        try:
            doc = docx.Document(io.BytesIO(contents))
            doc_parts = []

            for p in doc.paragraphs:
                if p.text.strip():
                    doc_parts.append(p.text.strip())

            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        doc_parts.append(" | ".join(row_cells))

            return "\n\n".join(doc_parts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from DOCX file: {e}")

    @staticmethod
    async def _extract_json(file: UploadFile) -> str:
        """
        Extract readable text from a JSON file.
        """
        import json
        contents = await file.read()
        await file.seek(0)
        try:
            data = json.loads(contents.decode("utf-8"))
            if isinstance(data, dict):
                parts = []
                for k, v in data.items():
                    if isinstance(v, (str, int, float, list)):
                        parts.append(f"{k}: {v}")
                return "\n".join(parts)
            elif isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict) and ("content" in data[0] or "url" in data[0]):
                    text_parts = []
                    for item in data:
                        title = item.get("title", "Untitled Page")
                        url = item.get("url", "")
                        content = item.get("content", "")
                        text_parts.append(f"Title: {title}\nURL: {url}\nContent:\n{content}\n")
                    return "\n---\n".join(text_parts)
                return "\n".join(str(item) for item in data)
            return json.dumps(data, indent=2)
        except Exception:
            return contents.decode("utf-8", errors="ignore")

    @staticmethod
    async def _extract_txt(file: UploadFile) -> str:
        """
        Extract text from a TXT file.
        """
        contents = await file.read()
        await file.seek(0)
        return contents.decode("utf-8")

    @staticmethod
    async def _extract_pdf(file: UploadFile) -> str:
        """
        Extract text from a PDF file using pypdf.
        """
        import io
        import pypdf

        contents = await file.read()
        await file.seek(0)

        reader = pypdf.PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    @staticmethod
    async def _extract_csv(file: UploadFile) -> str:
        """
        High-performance structured CSV extraction for fast RAG auto-ingestion & embedding.
        - Parses headers and maintains column-value associations.
        - Includes dataset overview profile (total records, column list).
        - Groups rows into structured Markdown tables with headers repeated across chunks.
        - Caps large datasets (up to 300 representative rows) to ensure sub-3-second ingestion.
        """
        import io
        import csv

        contents = await file.read()
        await file.seek(0)

        try:
            decoded = contents.decode("utf-8")
        except UnicodeDecodeError:
            decoded = contents.decode("latin-1", errors="ignore")

        reader = csv.reader(io.StringIO(decoded))
        rows = [row for row in reader if any(cell.strip() for cell in row)]
        if not rows:
            return ""

        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]
        total_data_rows = len(data_rows)

        if not headers:
            return ""

        # 1. Dataset Profile Header
        col_names_str = ", ".join(headers)
        output_parts = [
            f"# Dataset Overview: {file.filename}\n"
            f"- Total Records: {total_data_rows}\n"
            f"- Columns ({len(headers)}): {col_names_str}\n"
        ]

        # 2. Intelligent Row Capping for Fast Ingestion (up to 300 rows max)
        max_rows_to_embed = 300
        if total_data_rows > max_rows_to_embed:
            half = max_rows_to_embed // 2
            sampled_rows = data_rows[:half] + data_rows[-half:]
            output_parts.append(
                f"> [Note]: Large CSV dataset ({total_data_rows} rows). Showing top {half} and bottom {half} representative records for optimized retrieval.\n"
            )
        else:
            sampled_rows = data_rows

        # 3. Format into structured Markdown Tables with preserved headers (batches of 15 rows)
        batch_size = 15
        table_header = "| " + " | ".join(headers) + " |"
        table_sep = "| " + " | ".join(["---"] * len(headers)) + " |"

        for i in range(0, len(sampled_rows), batch_size):
            batch = sampled_rows[i:i + batch_size]
            table_lines = [
                f"\n### Records {i + 1} to {i + len(batch)} of {total_data_rows}",
                table_header,
                table_sep
            ]
            for row in batch:
                padded = [row[idx].strip().replace("\n", " ") if idx < len(row) else "" for idx in range(len(headers))]
                table_lines.append("| " + " | ".join(padded) + " |")
            output_parts.append("\n".join(table_lines))

        return "\n\n".join(output_parts)
