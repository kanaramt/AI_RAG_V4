from collections.abc import Generator

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from database.database import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
