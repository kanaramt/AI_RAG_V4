from backend import database
import os
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from uuid import uuid4
from typing import Dict, Any
from backend.utils.datetime_utils import ist_now

from backend.settings import settings
from backend.services.document_chunker import DocumentChunker
from backend.engines.document_intelligence.document_intelligence_engine import (
    DocumentIntelligenceEngine,
)
from backend.catalog.services.catalog_sync_service import (
    CatalogSyncService,
)
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_store.factory import VectorStoreFactory
from datetime import datetime

from backend.database.session import SessionLocal

from backend.services.document_management.document_sql_repository import (
    DocumentSQLRepository,
)
from backend.services.document_management.chunk_sql_repository import (
    ChunkSQLRepository,
)

from backend.services.ingestion_history.ingestion_history_sql_repository import (
    IngestionHistorySQLRepository,
)

from backend.schemas.knowledge.document_schema import (
    DocumentSchema,
)
from backend.schemas.knowledge.chunk_schema import (
    ChunkSchema,
)

from backend.database.models.ingestion_history import (
    IngestionHistoryModel,
)

class IngestionService:
    """
    Enterprise Ingestion Pipeline.
    Handles ingesting files, URLs, and pasted text.
    """

    @classmethod
    async def ingest_upload(cls, file, memory) -> Dict[str, Any]:
        """
        Ingest an uploaded file, write to vector database, register in SQLite,
        and synchronize the Knowledge Catalog.
        """

        # Save file to a persistent folder first
        upload_dir = settings.BACKEND_DIR / "data" / "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = upload_dir / file.filename
        contents = await file.read()
        await file.seek(0)

        with open(file_path, "wb") as f:
            f.write(contents)

        text = await DocumentIntelligenceEngine.extract_text(file)

        chunks = DocumentChunker.chunk_text(text)

        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings(chunks)

        vector_store = VectorStoreFactory.create()

        doc_id = str(uuid4())

        ids = [str(uuid4()) for _ in range(len(chunks))]

        metadatas = [
            {
                "source": file.filename,
                "doc_id": doc_id,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        vector_store.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        # Register document metadata in SQLite
        file_size = os.path.getsize(file_path)

        size_str = cls._format_size(file_size)

        memory.add_document(
            doc_id,
            file.filename,
            size_str,
            file.content_type or "text/plain",
            str(file_path),
        )

        # Save document metadata into PostgreSQL
        db = SessionLocal()

        try:
            repository = DocumentSQLRepository(db)

            repository.create(
                DocumentSchema(
                    document_id=doc_id,
                    title=file_path.name,
                    source_type="local_file",
                    source_name=file_path.name,
                    metadata={
                        "file_path": str(file_path),
                        "chunk_count": len(chunks),
                    },
                    content=text,
                    created_at=ist_now(),
                )
            )   
        finally:
            db.close()

        # -----------------------------
        # Synchronize Knowledge Catalog
        # -----------------------------
        CatalogSyncService().sync_document(
            doc_id=doc_id,
            source_name=file.filename,
            source_path=str(file_path),
            chunk_count=len(chunks),
            embedding_model=settings.EMBEDDING_MODEL,
            vector_store=settings.VECTOR_STORE,
        )

        # Rebuild KB Metadata Summary
        from backend.services.kb_metadata_service import KBMetadataService
        import asyncio
        asyncio.create_task(KBMetadataService.rebuild_metadata())

        return {
            "id": doc_id,
            "filename": file.filename,
            "status": "success",
            "message": f"Successfully indexed {len(chunks)} chunks.",
        }
    @classmethod
    async def ingest_local_file(cls, file_path: Path, memory) -> Dict[str, Any]:
        """
        Ingest a file that already exists in the local knowledge base.
        Supports: txt, pdf, csv, docx, xlsx, pptx, png, jpg, jpeg, bmp, tiff, webp
        """
        extension = file_path.suffix.lower()
        supported = {".txt", ".pdf", ".csv", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".json",
                     ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
        if extension not in supported:
            print(f"Skipping {file_path.name} (unsupported extension: {extension})")
            return None

        # MockFile wraps a local path as a FastAPI-compatible UploadFile
        class MockFile:
            def __init__(self, path: Path):
                self.filename = path.name
                self.path = path
                ext = path.suffix.lower()
                if ext == ".txt":
                    self.content_type = "text/plain"
                elif ext == ".json":
                    self.content_type = "application/json"
                elif ext == ".pdf":
                    self.content_type = "application/pdf"
                elif ext == ".csv":
                    self.content_type = "text/csv"
                elif ext in {".docx", ".doc"}:
                    self.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                elif ext in {".xlsx", ".xls"}:
                    self.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                elif ext in {".pptx", ".ppt"}:
                    self.content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                elif ext in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}:
                    self.content_type = f"image/{ext.lstrip('.')}"
                else:
                    self.content_type = "application/octet-stream"


            async def read(self):
                with open(self.path, "rb") as f:
                    return f.read()

            async def seek(self, offset):
                pass

        try:
            text = await DocumentIntelligenceEngine.extract_text(MockFile(file_path))
        except Exception as e:
            print(f"Could not extract text from {file_path.name}: {e}")
            return None

        if not text or not text.strip():
            print(f"No text extracted from {file_path.name}, skipping.")
            return None

        chunks = DocumentChunker.chunk_text(text)
        if not chunks:
            return None

        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings(chunks)

        vector_store = VectorStoreFactory.create()
        doc_id = str(uuid4())
        ids = [str(uuid4()) for i in range(len(chunks))]

        metadatas = [
            {
                "source": file_path.name,
                "doc_id": doc_id,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        vector_store.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        file_size = os.path.getsize(file_path)
        size_str = cls._format_size(file_size)
        memory.add_document(doc_id, file_path.name, size_str, "text/plain", str(file_path))
        print("STEP-1 REACHED POSTGRES SECTION")

        # --------------------------------------------------
        # Persist document + chunks to PostgreSQL
        # --------------------------------------------------
        db = SessionLocal()
        print("STEP-2 SESSION CREATED")
        try:
            print("STEP-3 CREATING DOCUMENT REPO")
            doc_repo = DocumentSQLRepository(db)
            print("STEP-4 SAVING DOCUMENT")
            doc_repo.create(
                DocumentSchema(
                    document_id=doc_id,
                    title=file_path.name,
                    source_type="local_file",
                    source_name=file_path.name,
                    metadata={
                        "file_path": str(file_path),
                        "chunk_count": len(chunks),
                    },
                    content=text,
                    created_at=ist_now(),
                )
            )
            print("STEP-5 DOCUMENT SAVED")
            print("STEP-6 CREATING CHUNK REPO")
            chunk_repo = ChunkSQLRepository(db)
            print("STEP-7 SAVING CHUNKS")
            chunk_repo.create_many(
                [
                    ChunkSchema(
                        chunk_id=ids[i],
                        document_id=doc_id,
                        chunk_index=i,
                        content=chunks[i],
                        metadata=metadatas[i],
                        created_at=ist_now(),
                    )
                    for i in range(len(chunks))
                ]
            )
            print("STEP-8 CHUNKS SAVED")

            db.add(
                IngestionHistoryModel(
                    document_id=doc_id,
                    action="INGEST",
                    source_type="local_file",
                    source_name=file_path.name,
                    status="SUCCESS",
                    details_json={
                        "chunk_count": len(chunks),
                        "file_path": str(file_path),
                    },
                )
            )

            db.commit()

            history_repo = IngestionHistorySQLRepository(db)

            history_repo.create(
                document_id=doc_id,
                asset_id=None,
                action="INGEST",
                source_type="local_file",
                source_name=file_path.name,
                status="SUCCESS",
                details_json={
                    "file_path": str(file_path),
                    "chunk_count": len(chunks),
                },
            )
            print("STEP-9 HISTORY SAVED")

        except Exception as e:
            print("POSTGRES ERROR:", str(e))
            history_repo = IngestionHistorySQLRepository(db)
            history_repo.create(
                document_id=doc_id,
                asset_id=None,
                action="INGEST",
                source_type="local_file",
                source_name=file_path.name,
                status="FAILED",
                details_json={
                    "error": str(e),
                    "file_path": str(file_path),
                },
            )
            raise

        finally:
            print("STEP-9 DB CLOSED")
            db.close()

        print("STEP-10 SYNCING CATALOG")
        CatalogSyncService().sync_document(
            doc_id=doc_id,
            source_name=file_path.name,
            source_path=str(file_path),
            chunk_count=len(chunks),
            embedding_model=settings.EMBEDDING_MODEL,
            vector_store=settings.VECTOR_STORE,
        )

        # Rebuild KB Metadata Summary
        from backend.services.kb_metadata_service import KBMetadataService
        import asyncio
        asyncio.create_task(KBMetadataService.rebuild_metadata())

        print(f"[IngestionService] Successfully ingested '{file_path.name}' -> {len(chunks)} chunks indexed.")
        return {
            "id": doc_id,
            "filename": file_path.name,
            "chunks": len(chunks)
        }


    @classmethod
    async def ingest_url(cls, url: str, memory) -> Dict[str, Any]:
        """
        Validate URL, fetch webpage, clean HTML (strip nav, menus, footers, ads, scripts),
        chunk, embed, index to vector database, and register metadata in SQLite.
        
        Returns:
            dict containing: status, doc_id, url, page_title, pages_loaded, chunks_created, processing_time_ms, vector_db_status
        """
        import asyncio
        from backend.services.ingestion.web_loader import WebLoader
        start_time = time.time()

        # 1. Fetch & clean webpage using WebLoader
        web_loader = WebLoader(url)
        documents = web_loader.load()
        doc = documents[0]

        cleaned_text = doc.page_content
        meta = doc.metadata
        page_title = meta.get("page_title", url)

        # 2. Chunk text using DocumentChunker
        doc_chunks = DocumentChunker.chunk_text(cleaned_text)
        if not doc_chunks:
            raise RuntimeError("No readable content chunks extracted from webpage.")

        # 3. Generate Embeddings using EmbeddingService
        embedding_service = EmbeddingService()
        embeddings = await asyncio.to_thread(embedding_service.generate_embeddings, doc_chunks)

        # 4. Store Embeddings in Vector Store (Qdrant & FAISS)
        vector_store = VectorStoreFactory.create()
        doc_id = str(uuid4())
        ids = [str(uuid4()) for _ in range(len(doc_chunks))]

        metadatas = [
            {
                "source": url,
                "source_url": url,
                "page_title": page_title,
                "doc_id": doc_id,
                "chunk_index": i,
                "timestamp": meta.get("timestamp")
            }
            for i in range(len(doc_chunks))
        ]
        vector_store.add_documents(ids, doc_chunks, embeddings, metadatas)

        # 5. Register in SQLite Memory
        size_str = cls._format_size(len(cleaned_text))
        memory.add_document(doc_id, f"URL: {page_title}", size_str, "text/html", url)

        # Register document metadata in SQLite/SQLAlchemy
        db = SessionLocal()
        try:
            repository = DocumentSQLRepository(db)
            repository.create(
                DocumentSchema(
                    document_id=doc_id,
                    title=f"URL: {page_title}",
                    source_type="website",
                    source_name=url,
                    metadata={
                        "url": url,
                        "chunk_count": len(doc_chunks),
                    },
                    content=cleaned_text,
                    created_at=ist_now(),
                )
            )
        finally:
            db.close()

        # Rebuild KB Metadata Summary
        from backend.services.kb_metadata_service import KBMetadataService
        asyncio.create_task(KBMetadataService.rebuild_metadata())

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        print(f"[IngestionService] Successfully ingested Webpage '{page_title}' ({url}) -> {len(doc_chunks)} chunks in {elapsed_ms}ms")


        return {
            "status": "success",
            "doc_id": doc_id,
            "url": url,
            "page_title": page_title,
            "pages_loaded": 1,
            "chunks_created": len(doc_chunks),
            "processing_time_ms": elapsed_ms,
            "vector_db_status": "indexed",
            "message": f"Successfully indexed '{page_title}' ({len(doc_chunks)} chunks)."
        }

    @classmethod
    async def ingest_pasted_content(cls, title: str, content: str, memory) -> bool:
        """
        Index clipboard pasted text.
        """
        try:
            import asyncio
            doc_chunks = DocumentChunker.chunk_text(content)
            embedding_service = EmbeddingService()
            embeddings = await asyncio.to_thread(embedding_service.generate_embeddings, doc_chunks)
            
            vector_store = VectorStoreFactory.create()
            doc_id = str(uuid4())
            ids = [str(uuid4()) for i in range(len(doc_chunks))]
            
            metadatas = [
                {
                    "source": title,
                    "doc_id": doc_id,
                    "chunk_index": i
                }
                for i in range(len(doc_chunks))
            ]
            vector_store.add_documents(ids, doc_chunks, embeddings, metadatas)
            
            size_str = cls._format_size(len(content))
            memory.add_document(doc_id, title, size_str, "text/plain", f"paste_{doc_id}")
            
            # Register document metadata in SQLite/SQLAlchemy
            db = SessionLocal()
            try:
                repository = DocumentSQLRepository(db)
                repository.create(
                    DocumentSchema(
                        document_id=doc_id,
                        title=title,
                        source_type="pasted_content",
                        source_name=title,
                        metadata={
                            "chunk_count": len(doc_chunks),
                        },
                        content=content,
                        created_at=ist_now(),
                    )
                )
            finally:
                db.close()

            # Rebuild KB Metadata Summary
            from backend.services.kb_metadata_service import KBMetadataService
            asyncio.create_task(KBMetadataService.rebuild_metadata())
            
            return True
        except Exception as e:
            print(f"Error indexing pasted content: {e}")
            return False

    @staticmethod
    def _format_size(size_in_bytes) -> str:
        if size_in_bytes == 0:
            return '0 Bytes'
        k = 1024
        sizes = ['Bytes', 'KB', 'MB']
        import math
        i = int(math.floor(math.log(size_in_bytes) / math.log(k))) if size_in_bytes > 0 else 0
        val = size_in_bytes / (k ** i)
        return f"{val:.1f} {sizes[i]}"