import traceback
import json
import os
import time
from database.session import SessionLocal
from services.document_management.document_sql_repository import DocumentSQLRepository
from engines.generation.generation_engine import GenerationEngine
from settings import settings

class KBMetadataService:
    METADATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "kb_metadata.json")

    @classmethod
    def get_metadata(cls) -> dict:
        os.makedirs(os.path.dirname(cls.METADATA_FILE), exist_ok=True)
        if os.path.exists(cls.METADATA_FILE):
            try:
                with open(cls.METADATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception as e:
                print(f"[KBMetadataService] Error reading metadata file: {e}")

        # Build metadata synchronously if file does not exist (using event loop if already running)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            metadata = {
                "kb_name": "Dynamic Knowledge Base",
                "kb_summary": "Scanning knowledge base documents...",
                "kb_topics": [],
                "categories": [],
                "document_titles": [],
                "major_themes": [],
                "document_count": 0,
                "last_indexed_timestamp": time.time()
            }
            asyncio.create_task(cls.rebuild_metadata())
            return metadata
        else:
            return loop.run_until_complete(cls.rebuild_metadata())

    @classmethod
    async def rebuild_metadata(cls) -> dict:
        print("[KBMetadataService] Rebuilding KB Metadata Summary...")
        db = SessionLocal()
        try:
            repo = DocumentSQLRepository(db)
            docs = repo.get_all()
        finally:
            db.close()

        if not docs:
            metadata = {
                "kb_name": "Empty Knowledge Base",
                "kb_summary": "No documents are currently indexed in the knowledge base.",
                "kb_topics": [],
                "categories": [],
                "document_titles": [],
                "major_themes": [],
                "document_count": 0,
                "last_indexed_timestamp": time.time()
            }
            cls.save_metadata(metadata)
            return metadata

        document_count = len(docs)
        document_titles = [doc.title for doc in docs if doc.title]
        categories_set = set()

        for doc in docs:
            meta = doc.metadata or {}
            if isinstance(meta, dict):
                cat = meta.get("category") or meta.get("genre") or meta.get("type")
                if cat:
                    categories_set.add(str(cat))

        doc_samples = []
        for doc in docs[:10]:
            doc_samples.append(f"Title: {doc.title}\nExcerpt: {doc.content[:250]}")

        samples_text = "\n\n".join(doc_samples)
        prompt = f"""
You are an Enterprise Knowledge Base Analyzer.
Analyze the following documents currently present in the knowledge base and generate a JSON metadata summary.

Documents Info:
{samples_text}

Provide a JSON object with exactly the following fields (nothing else, no formatting markdown other than JSON):
{{
  "kb_name": "A short descriptive name of this specific knowledge base (e.g. N8N Integration Docs, HR Policies)",
  "kb_summary": "A 2-3 sentence summary of what this knowledge base is about and what domain it covers.",
  "kb_topics": ["Topic 1", "Topic 2", ... (up to 8 main topics covered)],
  "major_themes": ["Theme 1", "Theme 2", ... (up to 5 major themes)]
}}
"""
        # Build intelligent deterministic fallback metadata
        top_titles = document_titles[:5]
        top_cats = list(categories_set)[:5]
        sample_topics = top_cats if top_cats else top_titles[:6]

        kb_name = f"Knowledge Base ({document_count} Documents)"
        if top_titles:
            kb_name = f"{top_titles[0]} & Related Documents" if len(top_titles) > 1 else str(top_titles[0])

        cat_str = f" across categories ({', '.join(top_cats)})" if top_cats else ""
        kb_summary = f"Enterprise knowledge base indexing {document_count} active document(s){cat_str} for semantic retrieval and question answering."
        kb_topics = sample_topics
        major_themes = top_cats if top_cats else ["Knowledge Repository", "Technical Documentation"]

        try:
            model_name = os.getenv("DEFAULT_CLOUD_MODEL") or os.getenv("LLM_MODEL") or settings.DEFAULT_MODEL
            print(f"[KBMetadataService] Attempting LLM analysis with model={model_name}")

            engine = GenerationEngine()
            response_text = await engine.generate(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            import re
            json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                kb_name = data.get("kb_name", kb_name)
                kb_summary = data.get("kb_summary", kb_summary)
                kb_topics = data.get("kb_topics", kb_topics)
                major_themes = data.get("major_themes", major_themes)
                print("[KBMetadataService] Successfully generated LLM summary for knowledge base.")
        except Exception as e:
            print(f"[KBMetadataService] Note: LLM metadata generation unavailable ({e}). Using deterministic fallback metadata.")

        metadata = {
            "kb_name": kb_name,
            "kb_summary": kb_summary,
            "kb_topics": kb_topics,
            "categories": list(categories_set),
            "document_titles": document_titles,
            "major_themes": major_themes,
            "document_count": document_count,
            "last_indexed_timestamp": time.time()
        }
        cls.save_metadata(metadata)
        return metadata

    @classmethod
    def save_metadata(cls, data: dict):
        try:
            os.makedirs(os.path.dirname(cls.METADATA_FILE), exist_ok=True)
            with open(cls.METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[KBMetadataService] Saved metadata summary to {cls.METADATA_FILE}")
        except Exception as e:
            print(f"[KBMetadataService] Error writing metadata: {e}")
