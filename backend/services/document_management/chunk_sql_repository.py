from sqlalchemy.orm import Session

from database.models.chunk_model import (
    ChunkModel,
)

from schemas.knowledge.chunk_schema import (
    ChunkSchema,
)


class ChunkSQLRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        chunk: ChunkSchema,
    ) -> ChunkSchema:

        model = ChunkModel(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            metadata_json=chunk.metadata,
            created_at=chunk.created_at,
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)

        return chunk

    def create_many(
        self,
        chunks: list[ChunkSchema],
    ) -> None:

        models = []

        for chunk in chunks:

            models.append(
                ChunkModel(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    metadata_json=chunk.metadata,
                    created_at=chunk.created_at,
                )
            )

        self.db.bulk_save_objects(
            models
        )

        self.db.commit()

    def get_by_document_id(
        self,
        document_id: str,
    ) -> list[ChunkSchema]:

        models = (
            self.db.query(
                ChunkModel
            )
            .filter(
                ChunkModel.document_id
                == document_id
            )
            .order_by(
                ChunkModel.chunk_index
            )
            .all()
        )

        return [
            self._to_schema(model)
            for model in models
        ]

    def _to_schema(
        self,
        model: ChunkModel,
    ) -> ChunkSchema:

        return ChunkSchema(
            chunk_id=model.chunk_id,
            document_id=model.document_id,
            chunk_index=model.chunk_index,
            content=model.content,
            metadata=model.metadata_json or {},
            created_at=model.created_at,
        )
