from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from utils.datetime_utils import ist_now
from database.base import Base


class CrawledWebsiteModel(Base):
    """
    SQLAlchemy model for tracked website crawlers and ingestion logs.
    """
    __tablename__ = "crawled_websites"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )
    root_url = Column(
        String,
        unique=True,
        nullable=False,
    )
    name = Column(
        String,
        nullable=False,
    )
    status = Column(
        String,
        nullable=False,
        default="pending",
    )  # pending, crawling, success, failed
    discovered_urls_count = Column(
        Integer,
        default=0,
    )
    crawled_pages_count = Column(
        Integer,
        default=0,
    )
    failed_pages_count = Column(
        Integer,
        default=0,
    )
    chunks_count = Column(
        Integer,
        default=0,
    )
    embeddings_count = Column(
        Integer,
        default=0,
    )
    error_message = Column(
        Text,
        nullable=True,
    )
    is_default = Column(
        Boolean,
        default=False,
    )
    is_enabled = Column(
        Boolean,
        default=True,
    )
    last_crawled_at = Column(
        DateTime,
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=ist_now,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=ist_now,
        onupdate=ist_now,
    )


class WebsiteConfigModel(Base):
    """
    SQLAlchemy model for website crawler configurations (e.g. allow_user_ingestion).
    """
    __tablename__ = "website_configs"

    key = Column(
        String,
        primary_key=True,
        index=True,
    )
    value = Column(
        String,
        nullable=False,
    )

