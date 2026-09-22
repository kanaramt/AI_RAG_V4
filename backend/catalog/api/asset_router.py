from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db

from catalog.repositories.asset_sql_repository import (
    AssetSQLRepository,
)

router = APIRouter(
    prefix="/catalog",
    tags=["Knowledge Assets"],
)


@router.get("/assets")
def get_assets(
    db: Session = Depends(get_db),
):
    repository = AssetSQLRepository(db)

    return repository.get_all()
