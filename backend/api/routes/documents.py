import os
import shutil
from typing import List
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dependencies import get_memory
from database.session import get_db
from settings import settings
from engines.ingestion.ingestion_engine import IngestionEngine

router = APIRouter()

# Schemas
class PasteSchema(BaseModel):
    title: str
    content: str

class UrlSchema(BaseModel):
    url: str


# --- Documents Endpoints ---

@router.get("")
async def list_documents(memory = Depends(get_memory)):
    """
    List all indexed documents registered in SQLite.
    """
    return memory.list_documents()

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(100),
    memory = Depends(get_memory)
):
    """
    Upload a list of documents and index them in Qdrant and FAISS,
    saving their metadata to SQLite database.
    """
    results = []
    for file in files:
        try:
            res = await IngestionEngine.ingest_file(file, memory)
            results.append({
                "name": file.filename,
                "status": "indexed"
            })
        except Exception as e:
            print(f"Error ingesting file {file.filename}: {e}")
            results.append({
                "name": file.filename,
                "status": "failed"
            })
    return results

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, memory = Depends(get_memory)):
    """
    Delete a document from Qdrant vectors and SQLite registry, and clean up local uploads.
    """
    doc = memory.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Delete points from Qdrant
    try:
        from services.vector_store.factory import VectorStoreFactory
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        vector_store = VectorStoreFactory.create()
        qdrant = vector_store.qdrant
        qdrant.client.delete(
            collection_name=qdrant.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            )
        )
    except Exception as e:
        print(f"Error deleting vectors for document {doc_id} from Qdrant: {e}")

    # 2. Delete local file from disk if applicable
    file_path = doc.get("path")
    if file_path and not file_path.startswith("http"):
        try:
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted local file: {file_path}")
        except Exception as e:
            print(f"Error deleting local file {file_path}: {e}")

    # 3. Delete registry from SQLite Memory
    memory.delete_document(doc_id)

    # 4. Delete registry from SQLAlchemy database
    try:
        from database.session import SessionLocal
        from database.models.document_model import DocumentModel
        db_session = SessionLocal()
        db_session.query(DocumentModel).filter(DocumentModel.document_id == doc_id).delete()
        db_session.commit()
        db_session.close()
    except Exception as e:
        print(f"Error deleting document {doc_id} registry from SQL: {e}")

    # 5. Trigger KB Metadata Rebuild
    try:
        from services.kb_metadata_service import KBMetadataService
        import asyncio
        asyncio.create_task(KBMetadataService.rebuild_metadata())
    except Exception as e:
        print(f"Error scheduling KB metadata rebuild: {e}")

    return {"status": "success"}


@router.delete("")
async def delete_all_documents(
    memory = Depends(get_memory),
    db: Session = Depends(get_db)
):
    """
    Delete all indexed documents, purge vector databases, clean up uploaded files on disk,
    reset crawled websites, and reset the SQLite tables.
    """
    # 1. Reset vector stores (Qdrant & FAISS)
    try:
        from services.vector_store.factory import VectorStoreFactory
        from qdrant_client.models import VectorParams, Distance
        
        vector_store = VectorStoreFactory.create()
        
        # Purge Qdrant collection
        qdrant = vector_store.qdrant
        qdrant.client.recreate_collection(
            collection_name=qdrant.collection_name,
            vectors_config=VectorParams(
                size=qdrant.VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print("Purged Qdrant collection successfully.")
    except Exception as e:
        print(f"Error purging Qdrant vector database: {e}")

    try:
        # Reset FAISS memory index
        from services.vector_store.factory import VectorStoreFactory
        vector_store = VectorStoreFactory.create()
        faiss_store = vector_store.faiss
        faiss_store._index = None
        faiss_store.documents = []
        faiss_store.metadatas = []
        print("Reset FAISS vector store successfully.")
    except Exception as e:
        print(f"Error resetting FAISS vector store: {e}")

    # 2. Clean up uploads directory on disk
    upload_dir = settings.BACKEND_DIR / "data" / "uploads"
    if upload_dir.exists():
        try:
            shutil.rmtree(upload_dir)
            os.makedirs(upload_dir, exist_ok=True)
            print("Purged uploaded files directory.")
        except Exception as e:
            print(f"Error clearing uploaded files directory: {e}")

    # 3. Clean up crawled websites directory on disk
    crawled_dir = settings.BACKEND_DIR / "data" / "crawled_websites"
    if crawled_dir.exists():
        try:
            shutil.rmtree(crawled_dir)
            os.makedirs(crawled_dir, exist_ok=True)
            print("Purged crawled websites directory.")
        except Exception as e:
            print(f"Error clearing crawled websites directory: {e}")

    # 4. Clean up aggregate json directory on disk
    json_dir = settings.BACKEND_DIR / "data" / "json"
    if json_dir.exists():
        try:
            shutil.rmtree(json_dir)
            os.makedirs(json_dir, exist_ok=True)
            print("Purged aggregate JSON directory.")
        except Exception as e:
            print(f"Error clearing aggregate JSON directory: {e}")

    # 5. Clear SQLite database registries
    try:
        # Clear document registries in memory SQLite connection
        memory.clear_all_documents()
    except Exception as e:
        print(f"Error clearing document registries from MemoryService: {e}")

    try:
        # Clear knowledge asset catalog & crawled websites registry
        from database.models.knowledge_asset import KnowledgeAssetModel
        from database.models.website_ingestion import CrawledWebsiteModel
        from database.models.document_model import DocumentModel
        
        # Delete everything
        db.query(KnowledgeAssetModel).delete()
        db.query(CrawledWebsiteModel).delete()
        db.query(DocumentModel).delete()
        db.commit()
        print("Purged catalog, website, and document database tables successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database tables: {e}")

    # Rebuild KB Metadata Summary
    try:
        from services.kb_metadata_service import KBMetadataService
        import asyncio
        asyncio.create_task(KBMetadataService.rebuild_metadata())
    except Exception as e:
        print(f"Error scheduling KB metadata rebuild: {e}")

    return {"status": "success", "message": "All documents, vector embeddings, local files, and crawler registries deleted successfully."}


# --- Direct Paste and URL endpoints ---

@router.post("/paste")
async def paste_content(data: PasteSchema, memory = Depends(get_memory)):
    """
    Directly index pasted clipboard text.
    """
    success = await IngestionEngine.ingest_pasted_content(
    data.title,
    data.content,
    memory,
)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to index pasted content")
    return {"status": "success"}

@router.post("/url")
async def index_url(data: UrlSchema, memory = Depends(get_memory)):
    """
    Validate, crawl, clean HTML, chunk, embed, and index a website URL into vector store.
    """
    try:
        res = await IngestionEngine.ingest_url(data.url, memory)
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except RuntimeError as run_err:
        raise HTTPException(status_code=422, detail=str(run_err))
    except Exception as e:
        print(f"[URL Ingestion Error] {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process URL: {str(e)}")


@router.post("/sync")
async def sync_knowledge_base(memory = Depends(get_memory)):
    """
    Scan backend/data/ and all format subfolders and ingest all supported files
    not already registered in SQLite memory registry.
    """
    from services.knowledge_base_loader import KnowledgeBaseLoader

    sync_result = await KnowledgeBaseLoader.sync_knowledge_base(memory)

    return {
        "synced": sync_result["synced_count"],
        "skipped": len(sync_result["errors"]),
        "files": sync_result["files"],
        "errors": sync_result["errors"],
        "message": f"Synced {sync_result['synced_count']} new file(s) from backend/data/ knowledge base."
    }


    
