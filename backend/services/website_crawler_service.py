import os
import json
import time
import hashlib
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from datetime import datetime
from utils.datetime_utils import ist_now
from uuid import uuid4

from settings import settings
from database.session import SessionLocal
from database.models.website_ingestion import CrawledWebsiteModel
from services.document_chunker import DocumentChunker
from services.embedding_service import EmbeddingService
from services.vector_store.factory import VectorStoreFactory
from catalog.schemas.knowledge_asset import SourceType, AssetStatus
from catalog.repositories.asset_sql_repository import AssetSQLRepository
from catalog.services.asset_service import AssetService


class WebsiteCrawlerService:
    """
    Service responsible for recursively crawling documentation websites,
    generating structured JSON documents, chunking with section headings,
    generating embeddings, indexing in Vector DB, and syncing to catalog.
    """

    CRAWL_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 EnterpriseRAGCrawler/1.0"
    )

    @staticmethod
    def get_website_id(url: str) -> str:
        return hashlib.md5(url.lower().strip().encode("utf-8")).hexdigest()

    @classmethod
    def start_crawl(cls, website_id: str, max_pages: int = 50, max_depth: int = 3):
        """
        Runs the crawling and indexing in a background thread to prevent blocking.
        """
        thread = threading.Thread(
            target=cls._crawl_and_index_sync,
            args=(website_id,),
            kwargs={"max_pages": max_pages, "max_depth": max_depth},
            daemon=True
        )
        thread.start()

    @classmethod
    def _crawl_and_index_sync(cls, website_id: str, max_pages: int = 50, max_depth: int = 3):
        """
        Synchronous worker executing the crawling, chunking, embedding, and indexing.
        """
        db = SessionLocal()
        website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
        if not website:
            db.close()
            return

        # Set status to crawling
        website.status = "crawling"
        website.error_message = None
        website.discovered_urls_count = 1
        website.crawled_pages_count = 0
        website.chunks_count = 0
        website.embeddings_count = 0
        db.commit()

        root_url = website.root_url
        parsed_root = urlparse(root_url)
        base_url = f"{parsed_root.scheme}://{parsed_root.netloc}"

        headers = {
            "User-Agent": cls.CRAWL_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        # 1. Read robots.txt
        rp = RobotFileParser()
        rp.set_url(urljoin(base_url, "/robots.txt"))
        try:
            rp.read()
        except Exception:
            rp = None

        discovered_urls = []

        # 2. Try parsing Sitemap
        sitemap_url = urljoin(base_url, "/sitemap.xml")
        try:
            resp = requests.get(sitemap_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                locs = soup.find_all("loc")
                for loc in locs:
                    loc_url = loc.get_text().strip()
                    loc_parsed = urlparse(loc_url)
                    if loc_parsed.netloc == parsed_root.netloc:
                        if rp is None or rp.can_fetch("*", loc_url):
                            discovered_urls.append(loc_url)
        except Exception as e:
            print(f"[Crawler Warning] Sitemap fetch failed for {root_url}: {e}")

        # Remove duplicates from sitemap discovery
        discovered_urls = list(set(discovered_urls))

        # 3. Fallback to recursive crawling if no sitemap urls found
        if not discovered_urls:
            queue = [root_url]
            visited = set()
            depths = {root_url: 0}

            while queue and len(discovered_urls) < max_pages:
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                discovered_urls.append(url)

                current_depth = depths.get(url, 0)
                if current_depth >= max_depth:
                    continue

                try:
                    # Update database with discovered count
                    website.discovered_urls_count = len(discovered_urls)
                    db.commit()

                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                        continue

                    soup = BeautifulSoup(resp.content, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        abs_url = urljoin(url, href).split("#")[0]
                        parsed_abs = urlparse(abs_url)
                        if parsed_abs.netloc == parsed_root.netloc and parsed_abs.scheme in ("http", "https"):
                            if abs_url not in visited and abs_url not in queue:
                                if rp is None or rp.can_fetch("*", abs_url):
                                    queue.append(abs_url)
                                    depths[abs_url] = current_depth + 1
                    
                    time.sleep(0.5)  # Be polite to the server
                except Exception as crawl_err:
                    print(f"[Crawler Error] Crawl step failed for {url}: {crawl_err}")
        else:
            # If sitemap was loaded, respect the page limit
            discovered_urls = discovered_urls[:max_pages]
            website.discovered_urls_count = len(discovered_urls)
            db.commit()

        # 4. Crawl discovered pages and extract content
        local_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id
        raw_pages_dir = local_dir / "raw_pages"
        chunked_pages_dir = local_dir / "chunked_pages"
        vector_embeddings_dir = local_dir / "vector_embeddings"

        os.makedirs(raw_pages_dir, exist_ok=True)
        os.makedirs(chunked_pages_dir, exist_ok=True)
        os.makedirs(vector_embeddings_dir, exist_ok=True)

        all_page_records = []
        all_page_chunks = []
        all_page_metadatas = []
        all_ids = []

        total_chunks = 0
        total_embeddings = 0
        failed_count = 0
        crawled_count = 0

        embedding_service = EmbeddingService()
        vector_store = VectorStoreFactory.create()

        for idx, page_url in enumerate(discovered_urls):
            try:
                resp = requests.get(page_url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    failed_count += 1
                    website.failed_pages_count = failed_count
                    db.commit()
                    continue

                title, sections, breadcrumb, headings_structure = cls._extract_structured_content(resp.text, page_url)
                
                # Full page text combined for raw JSON storage
                combined_content = "\n\n".join([f"## {sec['heading']}\n{sec['text']}" for sec in sections])
                
                page_id = hashlib.md5(page_url.lower().encode("utf-8")).hexdigest()

                # Raw JSON object representation (rich structure)
                page_record = {
                    "page_id": page_id,
                    "url": page_url,
                    "title": title,
                    "domain": parsed_root.netloc,
                    "source_type": "website",
                    "breadcrumb": breadcrumb,
                    "headings": headings_structure,
                    "content": combined_content,
                    "last_crawled": datetime.ist_now().isoformat()
                }

                # Save raw JSON inside raw_pages/
                raw_json_path = raw_pages_dir / f"{page_id}.json"
                with open(raw_json_path, "w", encoding="utf-8") as f:
                    json.dump(page_record, f, indent=2, ensure_ascii=False)

                all_page_records.append(page_record)
                crawled_count += 1
                website.crawled_pages_count = crawled_count
                db.commit()

                # Process chunks per section
                page_chunks = []
                for sec in sections:
                    sec_heading = sec["heading"]
                    sec_text = sec["text"]

                    if not sec_text.strip():
                        continue

                    sec_chunks = DocumentChunker.chunk_text(sec_text)
                    for chunk_idx, chunk_text in enumerate(sec_chunks):
                        chunk_id = str(uuid4())
                        token_count = len(chunk_text.split())

                        chunk_record = {
                            "chunk_id": chunk_id,
                            "page_id": page_id,
                            "url": page_url,
                            "title": title,
                            "section_heading": sec_heading,
                            "chunk_text": chunk_text,
                            "token_count": token_count
                        }
                        page_chunks.append(chunk_record)

                        all_ids.append(chunk_id)
                        all_page_chunks.append(chunk_text)

                        # Create metadata-aware chunk for Vector DB with full keys
                        all_page_metadatas.append({
                            "chunk_id": chunk_id,
                            "url": page_url,
                            "title": title,
                            "domain": parsed_root.netloc,
                            "section_heading": sec_heading,
                            "source_type": "website",
                            "source": website.root_url,
                            "doc_id": website_id,
                            "chunk_index": total_chunks,
                            "timestamp": datetime.ist_now().isoformat(),
                            "crawl_date": datetime.ist_now().isoformat()
                        })
                        total_chunks += 1

                # Save chunked page JSON inside chunked_pages/
                chunked_json_path = chunked_pages_dir / f"{page_id}_chunks.json"
                with open(chunked_json_path, "w", encoding="utf-8") as f:
                    json.dump(page_chunks, f, indent=2, ensure_ascii=False)

                # Update progress
                website.chunks_count = total_chunks
                db.commit()

                time.sleep(0.5)  # Rest between requests
            except Exception as page_err:
                failed_count += 1
                website.failed_pages_count = failed_count
                db.commit()
                print(f"[Crawler Page Error] Failed processing {page_url}: {page_err}")

        # Save aggregate JSON inside backend/data/json/
        if all_page_records:
            try:
                import re
                json_dir = settings.BACKEND_DIR / "data" / "json"
                os.makedirs(json_dir, exist_ok=True)
                slugified_name = re.sub(r'[^\w\s-]', '', website.name).strip()
                slugified_name = re.sub(r'[-\s]+', '_', slugified_name)
                aggregate_json_path = json_dir / f"{slugified_name}.json"
                with open(aggregate_json_path, "w", encoding="utf-8") as f:
                    json.dump(all_page_records, f, indent=2, ensure_ascii=False)
                print(f"[Crawler] Saved aggregate JSON dataset for website '{website.name}' to {aggregate_json_path}")
            except Exception as agg_err:
                print(f"[Crawler Warning] Failed saving aggregate JSON dataset: {agg_err}")

        # 5. Generate Embeddings & Store in Vector DB
        if all_page_chunks:
            try:
                # Generate embeddings using EmbeddingService
                embeddings = embedding_service.generate_embeddings(all_page_chunks)
                total_embeddings = len(embeddings)

                # Store in Qdrant & FAISS
                vector_store.add_documents(all_ids, all_page_chunks, embeddings, all_page_metadatas)

                # Save the embedding files per page (isolate storage)
                grouped_embeddings = {}
                for idx, chunk_text in enumerate(all_page_chunks):
                    meta = all_page_metadatas[idx]
                    page_hash_id = hashlib.md5(meta["url"].lower().encode("utf-8")).hexdigest()
                    
                    record = {
                        "chunk_id": all_ids[idx],
                        "page_id": page_hash_id,
                        "url": meta["url"],
                        "title": meta["title"],
                        "section_heading": meta["section_heading"],
                        "embedding": embeddings[idx],
                        "metadata": {
                            "url": meta["url"],
                            "title": meta["title"],
                            "domain": meta["domain"],
                            "section_heading": meta["section_heading"],
                            "source_type": meta["source_type"],
                            "crawl_date": meta["crawl_date"]
                        }
                    }
                    if page_hash_id not in grouped_embeddings:
                        grouped_embeddings[page_hash_id] = []
                    grouped_embeddings[page_hash_id].append(record)

                for page_hash_id, records in grouped_embeddings.items():
                    embedding_json_path = vector_embeddings_dir / f"{page_hash_id}_embeddings.json"
                    with open(embedding_json_path, "w", encoding="utf-8") as f:
                        json.dump(records, f, indent=2, ensure_ascii=False)

                website.embeddings_count = total_embeddings
                db.commit()
            except Exception as embed_err:
                print(f"[Crawler Error] Vector DB Ingestion failed: {embed_err}")
                website.status = "failed"
                website.error_message = f"Vector database write failed: {str(embed_err)}"
                db.commit()
                db.close()
                return

        # 6. Register in Knowledge Catalog
        try:
            asset_service = AssetService(AssetSQLRepository(db))
            asset = asset_service.repository.get_by_document_id(website_id)

            if asset is None:
                asset = asset_service.create_asset(
                    source_type=SourceType.WEBSITE,
                    source_name=website.root_url,
                    title=website.name,
                )

            asset.document_id = website_id
            asset.chunk_count = total_chunks
            asset.embedding_model = settings.EMBEDDING_MODEL
            asset.vector_store = settings.VECTOR_STORE
            asset.status = AssetStatus.ACTIVE
            asset_service.update_asset(asset)
        except Exception as catalog_err:
            print(f"[Crawler Catalog Error] Failed updating catalog sync: {catalog_err}")

        # 7. Finalize status
        website.status = "success"
        website.last_crawled_at = ist_now()
        db.commit()
        db.close()
    @classmethod
    def _extract_structured_content(cls, html_content: str, url: str) -> tuple[str, list[dict], str, list[dict]]:
        """
        Parses HTML content, stripping boilerplate (nav, footers, scripts, styles, cookie banners, etc.)
        and returns: title, sections list, breadcrumb, headings hierarchy list.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract Title
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc

        # Extract breadcrumb before decomposing elements
        breadcrumb = ""
        bc_selectors = [
            ".breadcrumb", ".breadcrumbs", "[aria-label='breadcrumb']", 
            ".td-breadcrumbs", ".breadcrumb-list", ".nav-breadcrumb"
        ]
        for sel in bc_selectors:
            bc_el = soup.select_one(sel)
            if bc_el:
                crumbs = [x.get_text().strip() for x in bc_el.find_all(["li", "a", "span"])]
                cleaned_crumbs = []
                for c in crumbs:
                    c_clean = c.strip()
                    if c_clean and c_clean not in cleaned_crumbs:
                        cleaned_crumbs.append(c_clean)
                if cleaned_crumbs:
                    breadcrumb = " > ".join(cleaned_crumbs)
                    break
        if not breadcrumb:
            # Fallback: parse URL path segments
            path_parts = [p for p in urlparse(url).path.split("/") if p]
            if path_parts:
                breadcrumb = " > ".join(path_parts)

        # Decompose breadcrumbs and other unwanted boilerplate elements
        unwanted_selectors = [
            "script", "style", "nav", "footer", "header", "aside",
            "noscript", "iframe", "svg", ".nav", ".navbar", ".footer",
            ".header", ".sidebar", ".menu", ".ad", ".advertisement",
            "#nav", "#footer", "#header", "#sidebar", "#menu", "#comments",
            ".cookie-banner", ".cookie-consent", "#cookie-banner", "#cookie-consent",
            ".feedback-widget", ".feedback-panel", "#feedback-section", ".feedback-container",
            ".was-this-page-helpful", "#was-this-page-helpful", ".helpful-section",
            ".additional-resources", "#additional-resources", ".related-resources",
            ".auth-message", ".unauthorized", "#access-warning"
        ]
        # Extend to include breadcrumb selectors to avoid repeating breadcrumb text in body content
        for sel in unwanted_selectors + bc_selectors:
            for element in soup.select(sel):
                element.decompose()

        # Find main content body
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content") or soup.find("body") or soup

        sections = []
        headings_structure = []
        current_heading = "Overview"
        current_text_blocks = []

        import re
        noise_patterns = [
            r"(?i)was this page helpful",
            r"(?i)need help with this topic",
            r"(?i)want to try using",
            r"(?i)access to this page requires authorization",
            r"(?i)you can try signing in or changing directories",
            r"(?i)cookie policy",
            r"(?i)all rights reserved",
            r"(?i)last updated on"
        ]

        block_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "table", "ul", "ol"]

        for tag in main_content.find_all(block_tags):
            tag_name = tag.name.lower()
            if tag_name.startswith("h"):
                heading_text = tag.get_text().strip()
                if heading_text:
                    if tag_name in ("h1", "h2", "h3"):
                        headings_structure.append({"text": heading_text, "level": tag_name})
                    if current_text_blocks:
                        sections.append({
                            "heading": current_heading,
                            "text": "\n\n".join(current_text_blocks)
                        })
                        current_text_blocks = []
                    current_heading = heading_text
            elif tag_name == "p":
                val = tag.get_text().strip()
                if val:
                    if any(re.search(pat, val) for pat in noise_patterns):
                        continue
                    current_text_blocks.append(val)
            elif tag_name == "pre":
                val = tag.get_text().strip()
                if val:
                    current_text_blocks.append(f"```\n{val}\n```")
            elif tag_name == "table":
                rows = []
                for tr in tag.find_all("tr"):
                    cols = [td.get_text().strip() for td in tr.find_all(["td", "th"])]
                    if cols:
                        rows.append(" | ".join(cols))
                if rows:
                    current_text_blocks.append("\n".join(rows))
            elif tag_name in ("ul", "ol"):
                items = []
                for li in tag.find_all("li"):
                    li_text = li.get_text().strip()
                    if li_text:
                        if any(re.search(pat, li_text) for pat in noise_patterns):
                            continue
                        items.append(f"- {li_text}")
                if items:
                    current_text_blocks.append("\n".join(items))

        if current_text_blocks:
            sections.append({
                "heading": current_heading,
                "text": "\n\n".join(current_text_blocks)
            })

        # Fallback to general text clean if no blocks gathered
        if not sections:
            raw_text = main_content.get_text(separator=" ")
            lines = (line.strip() for line in raw_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
            sections.append({
                "heading": "Overview",
                "text": cleaned_text
            })

        return title, sections, breadcrumb, headings_structure

    @classmethod
    def start_reindex(cls, website_id: str):
        """
        Runs the re-indexing of locally saved crawl data in a background thread to prevent blocking.
        """
        thread = threading.Thread(
            target=cls._reindex_sync,
            args=(website_id,),
            daemon=True
        )
        thread.start()

    @classmethod
    def _reindex_sync(cls, website_id: str):
        """
        Synchronous worker executing re-indexing from local raw pages JSON files.
        """
        db = SessionLocal()
        website = db.query(CrawledWebsiteModel).filter(CrawledWebsiteModel.id == website_id).first()
        if not website:
            db.close()
            return

        # Set status to crawling (to trigger frontend spinner and animation)
        website.status = "crawling"
        website.error_message = None
        db.commit()

        local_dir = settings.BACKEND_DIR / "data" / "crawled_websites" / website_id
        raw_pages_dir = local_dir / "raw_pages"
        chunked_pages_dir = local_dir / "chunked_pages"
        vector_embeddings_dir = local_dir / "vector_embeddings"

        # Make sure folders exist
        os.makedirs(raw_pages_dir, exist_ok=True)
        os.makedirs(chunked_pages_dir, exist_ok=True)
        os.makedirs(vector_embeddings_dir, exist_ok=True)

        # 1. Gather all raw page JSON files on disk
        import glob
        import shutil
        raw_files = glob.glob(os.path.join(raw_pages_dir, "*.json"))
        
        # If raw_pages folder is empty, fallback to checking legacy root JSON files
        if not raw_files:
            legacy_files = glob.glob(os.path.join(local_dir, "*.json"))
            raw_files = [f for f in legacy_files if os.path.basename(f) != f"{website_id}.json"]
            for lf in raw_files:
                try:
                    dest = raw_pages_dir / os.path.basename(lf)
                    shutil.copy(lf, dest)
                except Exception:
                    pass
            raw_files = glob.glob(os.path.join(raw_pages_dir, "*.json"))

        all_page_records = []
        all_page_chunks = []
        all_page_metadatas = []
        all_ids = []

        total_chunks = 0
        crawled_count = 0
        failed_count = 0

        embedding_service = EmbeddingService()
        vector_store = VectorStoreFactory.create()

        # Update discovered URLs count to files count
        website.discovered_urls_count = len(raw_files)
        website.crawled_pages_count = 0
        website.chunks_count = 0
        website.embeddings_count = 0
        db.commit()

        for file_path in raw_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    page_record = json.load(f)
                
                url = page_record.get("url")
                title = page_record.get("title")
                domain = page_record.get("domain")
                breadcrumb = page_record.get("breadcrumb", "")
                headings = page_record.get("headings", [])
                content = page_record.get("content", "")
                page_id = page_record.get("page_id", hashlib.md5(url.lower().encode("utf-8")).hexdigest())

                # Reconstruct sections from raw content
                sections = []
                current_section = None
                lines = content.splitlines()
                
                for line in lines:
                    if line.startswith("## "):
                        if current_section:
                            sections.append(current_section)
                        current_section = {
                            "heading": line[3:].strip(),
                            "text_blocks": []
                        }
                    else:
                        if current_section:
                            current_section["text_blocks"].append(line)
                        else:
                            current_section = {
                                "heading": "Overview",
                                "text_blocks": [line]
                            }
                if current_section:
                    sections.append(current_section)

                # Format sections
                formatted_sections = []
                for s in sections:
                    formatted_sections.append({
                        "heading": s["heading"],
                        "text": "\n".join(s["text_blocks"]).strip()
                    })

                page_chunks = []
                for sec in formatted_sections:
                    sec_heading = sec["heading"]
                    sec_text = sec["text"]

                    if not sec_text.strip():
                        continue

                    sec_chunks = DocumentChunker.chunk_text(sec_text)
                    for chunk_idx, chunk_text in enumerate(sec_chunks):
                        chunk_id = str(uuid4())
                        token_count = len(chunk_text.split())

                        chunk_record = {
                            "chunk_id": chunk_id,
                            "page_id": page_id,
                            "url": url,
                            "title": title,
                            "section_heading": sec_heading,
                            "chunk_text": chunk_text,
                            "token_count": token_count
                        }
                        page_chunks.append(chunk_record)

                        all_ids.append(chunk_id)
                        all_page_chunks.append(chunk_text)

                        all_page_metadatas.append({
                            "chunk_id": chunk_id,
                            "url": url,
                            "title": title,
                            "domain": domain,
                            "section_heading": sec_heading,
                            "source_type": "website",
                            "source": website.root_url,
                            "doc_id": website_id,
                            "chunk_index": total_chunks,
                            "timestamp": ist_now().isoformat(),
                            "crawl_date": ist_now().isoformat()
                        })
                        total_chunks += 1

                # Save chunked page JSON
                chunked_json_path = chunked_pages_dir / f"{page_id}_chunks.json"
                with open(chunked_json_path, "w", encoding="utf-8") as f:
                    json.dump(page_chunks, f, indent=2, ensure_ascii=False)

                # Update page record with page_id to ensure it's structured
                page_record["page_id"] = page_id
                all_page_records.append(page_record)

                crawled_count += 1
                website.crawled_pages_count = crawled_count
                website.chunks_count = total_chunks
                db.commit()

            except Exception as e:
                failed_count += 1
                website.failed_pages_count = failed_count
                db.commit()
                print(f"[Crawler Re-Index Error] Failed reading file {file_path}: {e}")

        # Save aggregate JSON
        if all_page_records:
            try:
                import re
                json_dir = settings.BACKEND_DIR / "data" / "json"
                os.makedirs(json_dir, exist_ok=True)
                slugified_name = re.sub(r'[^\w\s-]', '', website.name).strip()
                slugified_name = re.sub(r'[-\s]+', '_', slugified_name)
                aggregate_json_path = json_dir / f"{slugified_name}.json"
                with open(aggregate_json_path, "w", encoding="utf-8") as f:
                    json.dump(all_page_records, f, indent=2, ensure_ascii=False)
            except Exception as agg_err:
                print(f"[Crawler Re-Index Warning] Failed aggregate JSON save: {agg_err}")

        # 2. Generate Embeddings & Store in Vector DB
        if all_page_chunks:
            try:
                embeddings = embedding_service.generate_embeddings(all_page_chunks)
                total_embeddings = len(embeddings)

                # Store in Qdrant & FAISS
                vector_store.add_documents(all_ids, all_page_chunks, embeddings, all_page_metadatas)

                # Save embedding files
                grouped_embeddings = {}
                for idx, chunk_text in enumerate(all_page_chunks):
                    meta = all_page_metadatas[idx]
                    page_hash_id = hashlib.md5(meta["url"].lower().encode("utf-8")).hexdigest()
                    
                    record = {
                        "chunk_id": all_ids[idx],
                        "page_id": page_hash_id,
                        "url": meta["url"],
                        "title": meta["title"],
                        "section_heading": meta["section_heading"],
                        "embedding": embeddings[idx],
                        "metadata": {
                            "url": meta["url"],
                            "title": meta["title"],
                            "domain": meta["domain"],
                            "section_heading": meta["section_heading"],
                            "source_type": meta["source_type"],
                            "crawl_date": meta["crawl_date"]
                        }
                    }
                    if page_hash_id not in grouped_embeddings:
                        grouped_embeddings[page_hash_id] = []
                    grouped_embeddings[page_hash_id].append(record)

                for page_hash_id, records in grouped_embeddings.items():
                    embedding_json_path = vector_embeddings_dir / f"{page_hash_id}_embeddings.json"
                    with open(embedding_json_path, "w", encoding="utf-8") as f:
                        json.dump(records, f, indent=2, ensure_ascii=False)

                website.embeddings_count = total_embeddings
                db.commit()
            except Exception as embed_err:
                print(f"[Crawler Re-Index Error] Vector DB Ingestion failed: {embed_err}")
                website.status = "failed"
                website.error_message = f"Vector database write failed: {str(embed_err)}"
                db.commit()
                db.close()
                return

        # 3. Register/Update Knowledge Catalog
        try:
            from catalog.services.asset_service import AssetService
            from catalog.repositories.asset_sql_repository import AssetSQLRepository
            from catalog.schemas.knowledge_asset import AssetStatus
            from catalog.schemas.knowledge_asset import SourceType
            
            asset_service = AssetService(AssetSQLRepository(db))
            asset = asset_service.repository.get_by_document_id(website_id)

            if asset is None:
                asset = asset_service.create_asset(
                    source_type=SourceType.WEBSITE,
                    source_name=website.root_url,
                    title=website.name,
                )

            asset.document_id = website_id
            asset.chunk_count = total_chunks
            asset.embedding_model = settings.EMBEDDING_MODEL
            asset.vector_store = settings.VECTOR_STORE
            asset.status = AssetStatus.ACTIVE
            asset_service.update_asset(asset)
        except Exception as catalog_err:
            print(f"[Crawler Catalog Error] Failed updating catalog sync: {catalog_err}")

        # Finalize status
        website.status = "success"
        website.last_crawled_at = ist_now()
        db.commit()
        db.close()

