from typing import Any
from typing import Generic
from typing import Type
from typing import TypeVar

from sqlalchemy.orm import Session

from database.base import Base


ModelType = TypeVar(
    "ModelType",
    bound=Base,
)


class CRUDRepository(
    Generic[ModelType],
):
    """
    Generic enterprise CRUD repository.
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
        object_id: Any,
    ) -> ModelType | None:

        return self.db.get(
            self.model,
            object_id,
        )

    def get_all(
        self,
    ) -> list[ModelType]:

        return self.db.query(
            self.model,
        ).all()

    def update(
        self,
        obj: ModelType,
    ) -> ModelType:

        self.db.add(obj)

        self.db.commit()

        self.db.refresh(obj)

        return obj

    def delete(
        self,
        obj: ModelType,
    ) -> None:

        self.db.delete(obj)

        self.db.commit()

    def count(
        self,
    ) -> int:

        return self.db.query(
            self.model,
        ).count()
