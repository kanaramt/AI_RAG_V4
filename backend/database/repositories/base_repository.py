from typing import Generic
from typing import Type
from typing import TypeVar

from sqlalchemy.orm import Session

from database.base import Base


ModelType = TypeVar(
    "ModelType",
    bound=Base,
)


class BaseRepository(
    Generic[ModelType],
):
    """
    Generic SQLAlchemy Repository.
    """

    def __init__(
        self,
        db: Session,
        model: Type[ModelType],
    ):

        self.db = db

        self.model = model

    def create(
        self,
        obj: ModelType,
    ) -> ModelType:

        self.db.add(obj)

        self.db.commit()

        self.db.refresh(obj)

        return obj

    def get(
        self,
        object_id: int,
    ) -> ModelType | None:

        return self.db.get(
            self.model,
            object_id,
        )

    def get_all(
        self,
    ) -> list[ModelType]:

        return (
            self.db.query(
                self.model,
            )
            .all()
        )

    def delete(
        self,
        obj: ModelType,
    ) -> None:

        self.db.delete(obj)

        self.db.commit()
