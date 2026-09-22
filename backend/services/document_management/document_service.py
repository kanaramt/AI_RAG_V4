from database.session import (
    SessionLocal,
)

from schemas.knowledge.document_schema import (
    DocumentSchema,
)

from schemas.knowledge.chunk_schema import (
    ChunkSchema,
)

from services.document_management.document_sql_repository import (
    DocumentSQLRepository,
)

from services.document_management.chunk_sql_repository import (
    ChunkSQLRepository,
)


class DocumentService:

    def create_document(
        self,
        document: DocumentSchema,
    ) -> DocumentSchema:

        db = SessionLocal()

        try:

            repository = (
                DocumentSQLRepository(
                    db
                )
            )

            return repository.create(
                document
            )

        finally:

            db.close()

    def get_document(
        self,
        document_id: str,
    ) -> DocumentSchema | None:

        db = SessionLocal()

        try:

            repository = (
                DocumentSQLRepository(
                    db
                )
            )

            return (
                repository.get_by_document_id(
                    document_id
                )
            )

        finally:

            db.close()

    def save_chunks(
        self,
        chunks: list[ChunkSchema],
    ) -> None:

        db = SessionLocal()

        try:

            repository = (
                ChunkSQLRepository(
                    db
                )
            )

            repository.create_many(
                chunks
            )

        finally:

            db.close()

    def get_chunks(
        self,
        document_id: str,
    ) -> list[ChunkSchema]:

        db = SessionLocal()

        try:

            repository = (
                ChunkSQLRepository(
                    db
                )
            )

            return (
                repository.get_by_document_id(
                    document_id
                )
            )

        finally:

            db.close()
