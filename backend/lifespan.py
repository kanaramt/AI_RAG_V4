import asyncio
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

#from database.base import Base
#from database.database import engine
#from database.session import SessionLocal
from database.base import Base
from database.database import engine
from database.session import SessionLocal
# Import all SQLAlchemy models here
#from database.models import *
#from services.knowledge_base_loader import KnowledgeBaseLoader
#from memory.memory_service import MemoryService
from database.models import *
from services.knowledge_base_loader import KnowledgeBaseLoader
from memory.memory_service import MemoryService



def safe_print(msg: str):
    """
    Print helper that forces UTF-8 output on Windows (cp1252 cannot encode emojis).
    Falls back to ASCII-safe printing if reconfigure is unavailable.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


async def auto_sync_watcher(memory: MemoryService, interval_seconds: float = 10.0):
    """
    Background worker that periodically checks backend/data/ and its format subfolders
    for newly added or modified documents and auto-ingests & embeds them.
    """
    safe_print(f"[KnowledgeBaseWatcher] Background watcher started (scanning backend/data/ every {interval_seconds}s)...")
    while True:
        try:
            await KnowledgeBaseLoader.sync_knowledge_base(memory)
        except asyncio.CancelledError:
            safe_print("[KnowledgeBaseWatcher] Background watcher stopped.")
            break
        except Exception as e:
            safe_print(f"[KnowledgeBaseWatcher] Sync error: {e}")
        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Application startup/shutdown context manager.
    """
    # Create all database tables
    Base.metadata.create_all(
        bind=engine,
    )

    # Populate default seed websites in DB if not exist
    db = SessionLocal()
    try:
        # Dynamically add failed_pages_count column if it does not exist (backward compatibility)
        try:
            from sqlalchemy import text
            db.execute(text("ALTER TABLE crawled_websites ADD COLUMN failed_pages_count INTEGER DEFAULT 0"))
            db.commit()
            safe_print("[Lifespan] Added failed_pages_count column to crawled_websites database table.")
        except Exception as e:
            safe_print(f"[Lifespan Migration Warning] Could not alter table: {e}")
            pass  # Column already exists

        #from database.models.website_ingestion import CrawledWebsiteModel
        #from services.website_crawler_service import WebsiteCrawlerService
        from database.models.website_ingestion import CrawledWebsiteModel
        from services.website_crawler_service import WebsiteCrawlerService

        default_seeds = [
            {"url": "https://docs.langchain.com", "name": "LangChain Documentation"},
            {"url": "https://docs.crewai.com", "name": "CrewAI Documentation"},
            {"url": "https://fastapi.tiangolo.com", "name": "FastAPI Documentation"}
        ]
        for seed in default_seeds:
            wid = WebsiteCrawlerService.get_website_id(seed["url"])
            exists = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == wid).first()
            if not exists:
                website = CrawledWebsiteModel(
                    id=wid,
                    root_url=seed["url"],
                    name=seed["name"],
                    status="pending",
                    is_default=True,
                    is_enabled=True
                )
                db.add(website)
        db.commit()
        safe_print("[Lifespan] Initialized default seed website definitions in SQLite.")
    except Exception as init_err:
        safe_print(f"Error initializing default seeds: {init_err}")
    finally:
        db.close()

    # Initialize shared memory service
    memory = MemoryService()

    async def _initial_kb_sync():
        """Run initial KB discovery after server is already up and accepting requests."""
        await asyncio.sleep(2)  # Brief pause so server fully binds port first
        safe_print("\n[Lifespan] Running initial Knowledge Base discovery and auto-embedding (background)...")
        try:
            await KnowledgeBaseLoader.sync_knowledge_base(memory)
            safe_print("[Lifespan] Initial Knowledge Base sync complete.")
        except Exception as e:
            safe_print(f"[Lifespan] Initial Knowledge Base sync error: {e}")

    # Launch background auto-sync watcher loop (includes initial sync above)
    initial_sync_task = asyncio.create_task(_initial_kb_sync())
    watcher_task = asyncio.create_task(auto_sync_watcher(memory, interval_seconds=10.0))

    # Server is now ready — yield immediately so port 8000 opens without delay
    yield

    # Shutdown hooks
    initial_sync_task.cancel()
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass
