from sqlalchemy import create_engine

from settings import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,

    pool_pre_ping=True,
    pool_recycle=300,
)