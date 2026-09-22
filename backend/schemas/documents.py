from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """
    Response returned after a document is uploaded.
    """

    filename: str = Field(
        ...,
        description="Uploaded file name"
    )

    status: str = Field(
        ...,
        description="Upload status"
    )

    message: str = Field(
        ...,
        description="Upload result"
    )
