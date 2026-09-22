import json
from pathlib import Path

from database.session import (
    SessionLocal,
)

from services.document_management.document_sql_repository import (
    DocumentSQLRepository,
)

from services.document_management.chunk_sql_repository import (
    ChunkSQLRepository,
)


class JSONExportService:

    def export_all_documents(
        self,
        output_file: str,
    ) -> str:

        db = SessionLocal()

        try:

            document_repository = (
                DocumentSQLRepository(db)
            )

            chunk_repository = (
                ChunkSQLRepository(db)
            )

            documents = (
                document_repository.get_all()
            )

            dataset = []

            for document in documents:

                chunks = (
                    chunk_repository.get_by_document_id(
                        document.document_id
                    )
                )

                dataset.append(
                    {
                        "document": (
                            document.model_dump()
                        ),
                        "chunks": [
                            chunk.model_dump()
                            for chunk in chunks
                        ],
                    }
                )

            Path(
                output_file
            ).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with open(
                output_file,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    dataset,
                    file,
                    indent=4,
                    default=str,
                )

            return output_file

        finally:

            db.close()
