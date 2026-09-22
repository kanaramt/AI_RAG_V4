
from pathlib import Path

from fastapi import HTTPException, UploadFile


class DocumentValidator:
    """
    Validates uploaded documents before they enter
    the RAG ingestion pipeline.
    """

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".xlsx",
        ".pptx",
    }

    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

    @classmethod
    def validate_filename(cls, file: UploadFile) -> None:
        """
        Validate the uploaded file name and extension.
        """

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing."
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type '{extension}'. "
                    f"Allowed types: {', '.join(sorted(cls.ALLOWED_EXTENSIONS))}"
                ),
            )
    @classmethod
    async def validate_file_size(cls, file: UploadFile) -> None:
        """
        Validate uploaded file size.
        """

        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        if len(contents) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds the maximum size of {cls.MAX_FILE_SIZE // (1024 * 1024)} MB."
            )

        # Reset file pointer so later stages can read the file again
        await file.seek(0)
