import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.settings import settings
from backend.engines.ingestion.ingestion_engine import IngestionEngine


class KnowledgeBaseLoader:
    """
    Enterprise Knowledge Base Loader & Auto-Sync Engine.

    Responsibilities:
    - Recursively scan backend/data and all format subfolders (pdf, docx, txt, csv, xlsx, pptx, images, etc.)
    - Filter supported document extensions while ignoring database and system files
    - Compare discovered files against indexed paths in SQLite memory
    - Ingest and embed new or updated documents into Qdrant vector store and SQLite registry
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".xlsx",
        ".xls",
        ".csv",
        ".txt",
        ".json",
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".webp",
    }


    @classmethod
    def get_data_directory(cls) -> Path:
        data_dir = settings.BACKEND_DIR / "data"
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @classmethod
    def discover_files(cls) -> List[Path]:
        """
        Discover all supported files under backend/data and all subdirectories.
        """
        discovered_files = []
        data_directory = cls.get_data_directory()

        if not data_directory.exists():
            return discovered_files

        for file in data_directory.rglob("*"):
            if not file.is_file():
                continue
            # Ignore hidden files, .gitkeep, and SQLite DB files
            if file.name.startswith(".") or file.suffix.lower() in {".db", ".db-wal", ".db-shm"}:
                continue
            # Ignore processed directory outputs or dataset logs
            if "processed" in file.parts or "query_dataset" in file.parts:
                continue


            if file.suffix.lower() in cls.SUPPORTED_EXTENSIONS:
                discovered_files.append(file)

        return sorted(discovered_files)

    @classmethod
    async def sync_knowledge_base(cls, memory: Optional[Any] = None) -> Dict[str, Any]:
        """
        Scan backend/data/ and all format subfolders, auto-ingesting and embedding
        any files not yet indexed in SQLite memory.
        """
        if memory is None:
            from backend.memory.memory_service import MemoryService
            memory = MemoryService()

        # Get existing indexed documents from SQLite memory
        existing_docs = memory.list_documents()
        existing_paths = {str(Path(d.get("path", "")).resolve()) for d in existing_docs if d.get("path")}
        existing_names = {d.get("name", "") for d in existing_docs}

        files = cls.discover_files()
        synced_files = []
        errors = []

        for file_path in files:
            abs_path_str = str(file_path.resolve())
            
            # Skip if already indexed by exact path or filename
            if abs_path_str in existing_paths or file_path.name in existing_names:
                continue

            print(f"[KnowledgeBaseLoader] Auto-ingesting & embedding: {file_path.relative_to(settings.BACKEND_DIR)}")
            try:
                result = await IngestionEngine.ingest_local_file(file_path, memory)
                if result:
                    synced_files.append(file_path.name)
                    existing_paths.add(abs_path_str)
                    existing_names.add(file_path.name)
                else:
                    errors.append(f"{file_path.name}: No text extracted")
            except Exception as e:
                print(f"[KnowledgeBaseLoader] Error ingesting '{file_path.name}': {e}")
                errors.append(f"{file_path.name}: {str(e)}")

        if synced_files:
            print(f"[KnowledgeBaseLoader] Auto-synced {len(synced_files)} new file(s) into knowledge base!")


        return {
            "synced_count": len(synced_files),
            "files": synced_files,
            "errors": errors,
            "total_discovered": len(files)
        }

    @classmethod
    async def ingest_all(cls):
        """
        Legacy CLI entry point for full sync.
        """
        return await cls.sync_knowledge_base()


if __name__ == "__main__":
    asyncio.run(KnowledgeBaseLoader.ingest_all())