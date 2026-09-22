
from sqlalchemy.orm import Session

from database.models.document_model import (
    DocumentModel,
)

from schemas.knowledge.document_schema import (
    DocumentSchema,
)


class DocumentSQLRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        document: DocumentSchema,
    ) -> DocumentSchema:

        model = DocumentModel(
            document_id=document.document_id,
            title=document.title,
            source_type=document.source_type,
            source_name=document.source_name,
            metadata_json=document.metadata,
            content=document.content,
            created_at=document.created_at,
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)

        return document

    def get_all(
        self,
    ) -> list[DocumentSchema]:

        models = self.db.query(
            DocumentModel
        ).all()

        return [
            self._to_schema(model)
            for model in models
        ]

    def _to_schema(
        self,
        model: DocumentModel,
    ) -> DocumentSchema:

        return DocumentSchema(
            document_id=model.document_id,
            title=model.title,
            source_type=model.source_type,
            source_name=model.source_name,
            metadata=model.metadata_json or {},
            content=model.content,
            created_at=model.created_at,
        )

    def get_by_document_id(
        self,
        document_id: str,
    ) -> DocumentSchema | None:

        model = (
            self.db.query(
                DocumentModel
            )
            .filter(
                DocumentModel.document_id
                == document_id
            )
            .first()
        )

        if not model:
            return None

        return self._to_schema(
            model
        )
