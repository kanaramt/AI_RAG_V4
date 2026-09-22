import os
import shutil
import glob
import json
from urllib.parse import urlparse
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.session import get_db
from database.models.website_ingestion import CrawledWebsiteModel, WebsiteConfigModel
from services.website_crawler_service import WebsiteCrawlerService
from settings import settings
from services.vector_store.factory import VectorStoreFactory
from catalog.repositories.asset_sql_repository import AssetSQLRepository
from catalog.services.asset_service import AssetService

router = APIRouter()

class AddWebsiteSchema(BaseModel):
    url: str
    name: str
    is_default: Optional[bool] = False

class UpdateConfigSchema(BaseModel):
    allow_user_ingestion: bool


@router.get("")
@router.get("/")
async def list_websites(db: Session = Depends(get_db)):
    """
    List all registered website crawlers and their statuses.
    """
    websites = db.query(CrawledWebsiteModel).all()
    return [
        {
            "id": w.id,
            "root_url": w.root_url,
            "name": w.name,
            "status": w.status,
            "discovered_urls_count": w.discovered_urls_count,
            "crawled_pages_count": w.crawled_pages_count,
            "chunks_count": w.chunks_count,
            "embeddings_count": w.embeddings_count,
            "error_message": w.error_message,
            "is_default": w.is_default,
            "is_enabled": w.is_enabled,
            "last_crawled_at": w.last_crawled_at.isoformat() if w.last_crawled_at else None,
            "created_at": w.created_at.isoformat(),
        }
        for w in websites
    ]


@router.post("")
@router.post("/")
async def add_website(payload: AddWebsiteSchema, db: Session = Depends(get_db)):
    """
    Register a new website crawler and start the crawling process.
    """
    url_clean = payload.url.strip()
    name_clean = payload.name.strip()
    
    if not url_clean or not name_clean:
        raise HTTPException(status_code=400, detail="URL and friendly name are required.")

    # Check config: is user ingestion allowed?
    allow_user_config = db.query(WebsiteConfigModel).filter(WebsiteConfigModel.key == "allow_user_ingestion").first()
    allow_user = True
    if allow_user_config and allow_user_config.value.lower() == "false":
        allow_user = False

    if not allow_user and not payload.is_default:
        raise HTTPException(status_code=403, detail="User website ingestion is currently disabled by Admin.")

    website_id = WebsiteCrawlerService.get_website_id(url_clean)

    # Check if duplicate
    existing = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Website with URL '{url_clean}' is already registered.")

    website = CrawledWebsiteModel(
        id=website_id,
        root_url=url_clean,
        name=name_clean,
        status="pending",
        is_default=payload.is_default,
        is_enabled=True,
    )
    db.add(website)
    db.commit()

    # Trigger async crawling
    WebsiteCrawlerService.start_crawl(website_id, max_pages=50, max_depth=3)

    return {"status": "success", "message": "Crawler registered and started.", "id": website_id}


@router.post("/{website_id}/recrawl")
async def recrawl_website(website_id: str, db: Session = Depends(get_db)):
    """
    Trigger re-crawling and re-indexing of an existing website.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    website.status = "pending"
    db.commit()

    # Start crawl in background
    WebsiteCrawlerService.start_crawl(website_id, max_pages=50, max_depth=3)

    return {"status": "success", "message": "Recrawling triggered."}


@router.post("/{website_id}/reindex")
async def reindex_website(website_id: str, db: Session = Depends(get_db)):
    """
    Trigger vector embedding generation and ingestion directly from local raw JSON pages without re-crawling.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    website.status = "pending"
    db.commit()

    # Start reindexing in background
    WebsiteCrawlerService.start_reindex(website_id)

    return {"status": "success", "message": "Re-indexing triggered."}


@router.delete("/{website_id}")
async def delete_website(website_id: str, db: Session = Depends(get_db)):
    """
    Unregister a website crawler, delete local files, vectors from Vector DB, and clear catalog.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    # 1. Delete points from Vector DB (Qdrant)
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        vector_store = VectorStoreFactory.create()
        qdrant = vector_store.qdrant
        qdrant.client.delete(
            collection_name=qdrant.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=website_id)
                    )
                ]
            )
        )
    except Exception as q_err:
        print(f"[Vector delete warning] Could not purge vectors for website {website_id}: {q_err}")

    # 2. Cleanup local folder on disk
    local_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id
    if local_dir.exists():
        try:
            shutil.rmtree(local_dir)
        except Exception as f_err:
            print(f"[File cleanup warning] Failed deleting {local_dir}: {f_err}")

    # 2b. Delete aggregate JSON from backend/data/json/
    try:
        import re
        slugified_name = re.sub(r'[^\w\s-]', '', website.name).strip()
        slugified_name = re.sub(r'[-\s]+', '_', slugified_name)
        agg_path = settings.BACKEND_DIR / "data" / "json" / f"{slugified_name}.json"
        if agg_path.exists():
            agg_path.unlink()
    except Exception as agg_del_err:
        print(f"[File cleanup warning] Failed deleting aggregate JSON: {agg_del_err}")

    # 3. Delete from Knowledge Catalog
    try:
        asset_service = AssetService(AssetSQLRepository(db))
        asset = asset_service.repository.get_by_document_id(website_id)
        if asset:
            asset_service.delete_asset(asset.asset_id)
    except Exception as c_err:
        print(f"[Catalog delete warning] Failed deleting catalog asset: {c_err}")

    # 4. Delete from local registry SQLite
    db.delete(website)
    db.commit()

    return {"status": "success", "message": "Website and all indexed vectors successfully removed."}


@router.get("/{website_id}/status")
async def get_website_status(website_id: str, db: Session = Depends(get_db)):
    """
    Get live progress status for a specific crawler session.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    return {
        "status": website.status,
        "discovered_urls_count": website.discovered_urls_count,
        "crawled_pages_count": website.crawled_pages_count,
        "chunks_count": website.chunks_count,
        "embeddings_count": website.embeddings_count,
        "error_message": website.error_message,
        "last_crawled_at": website.last_crawled_at.isoformat() if website.last_crawled_at else None,
    }


@router.get("/{website_id}/download")
async def download_website_json(website_id: str, db: Session = Depends(get_db)):
    """
    Stream aggregated extracted raw JSON pages for the website.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    local_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id
    if not local_dir.exists():
        return JSONResponse(content=[], status_code=200)

    aggregated_records = []
    json_files = glob.glob(os.path.join(local_dir, "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                aggregated_records.append(json.load(f))
        except Exception as e:
            print(f"Error reading JSON file {file_path}: {e}")

    domain = urlparse(website.root_url).netloc.replace(".", "_")
    return JSONResponse(
        content=aggregated_records,
        headers={"Content-Disposition": f"attachment; filename={domain}_crawled_dataset.json"}
    )


@router.get("/{website_id}/view/raw")
async def view_website_raw_json(website_id: str, db: Session = Depends(get_db)):
    """
    View aggregated raw pages JSON inline in a new tab.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    raw_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id / "raw_pages"
    if not raw_dir.exists():
        # Fallback: check legacy root files if any
        local_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id
        if local_dir.exists():
            json_files = glob.glob(os.path.join(local_dir, "*.json"))
            aggregated = []
            for f_path in json_files:
                try:
                    with open(f_path, "r", encoding="utf-8") as f:
                        aggregated.append(json.load(f))
                except Exception:
                    pass
            return JSONResponse(content=aggregated, status_code=200)
        return JSONResponse(content=[], status_code=200)

    aggregated = []
    json_files = glob.glob(os.path.join(raw_dir, "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                aggregated.append(json.load(f))
        except Exception:
            pass

    return JSONResponse(content=aggregated, status_code=200)


@router.get("/{website_id}/view/chunked")
async def view_website_chunked_json(website_id: str, db: Session = Depends(get_db)):
    """
    View aggregated chunked JSON inline in a new tab.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    chunked_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id / "chunked_pages"
    if not chunked_dir.exists():
        return JSONResponse(content=[], status_code=200)

    aggregated = []
    json_files = glob.glob(os.path.join(chunked_dir, "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                aggregated.extend(json.load(f))
        except Exception:
            pass

    return JSONResponse(content=aggregated, status_code=200)


@router.get("/{website_id}/view/embeddings")
async def view_website_embeddings_json(website_id: str, db: Session = Depends(get_db)):
    """
    View aggregated vector embeddings JSON inline in a new tab.
    """
    website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    embeddings_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id / "vector_embeddings"
    if not embeddings_dir.exists():
        return JSONResponse(content=[], status_code=200)

    aggregated = []
    json_files = glob.glob(os.path.join(embeddings_dir, "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                aggregated.extend(json.load(f))
        except Exception:
            pass

    return JSONResponse(content=aggregated, status_code=200)


@router.get("/config/ingestion")
async def get_config(db: Session = Depends(get_db)):
    """
    Get global configs for user website ingestion.
    """
    allow_user_config = db.query(WebsiteConfigModel).filter(WebsiteConfigModel.key == "allow_user_ingestion").first()
    allow_user = True
    if allow_user_config and allow_user_config.value.lower() == "false":
        allow_user = False
    return {"allow_user_ingestion": allow_user}


@router.post("/config/ingestion")
async def save_config(payload: UpdateConfigSchema, db: Session = Depends(get_db)):
    """
    Toggle user website ingestion permissions (Admin toggle).
    """
    cfg = db.query(WebsiteConfigModel).filter(WebsiteConfigModel.key == "allow_user_ingestion").first()
    val_str = "true" if payload.allow_user_ingestion else "false"
    if not cfg:
        cfg = WebsiteConfigModel(key="allow_user_ingestion", value=val_str)
        db.add(cfg)
    else:
        cfg.value = val_str
    db.commit()
    return {"status": "success", "allow_user_ingestion": payload.allow_user_ingestion}

