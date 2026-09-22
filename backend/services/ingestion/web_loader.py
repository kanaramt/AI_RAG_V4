"""
WebLoader Module
Enterprise Webpage Loader and Scraper for RAG Pipeline.

Provides robust URL validation, HTTP downloading, SSL error handling,
HTML cleaning (stripping navigation, menus, ads, footers, scripts, styles),
LangChain Document object creation, and rich metadata extraction.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class WebLoader:
    """
    Production-level Website URL Loader.
    
    Responsibilities:
    - URL syntax & scheme validation
    - Webpage fetching with custom User-Agent and timeout controls
    - HTML cleaning (stripping navs, footers, scripts, styles, ads)
    - LangChain Document object generation with structured metadata
    """

    def __init__(
        self,
        url: str,
        timeout: int = 15,
        user_agent: Optional[str] = None
    ):
        """
        Initialize WebLoader with target URL.
        """
        self.url = url.strip() if url else ""
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        self._validate_url()

    def _validate_url(self) -> None:
        """
        Validate URL syntax and scheme.
        Raises ValueError if invalid.
        """
        if not self.url:
            raise ValueError("URL cannot be empty.")

        parsed = urlparse(self.url)
        if not parsed.scheme or parsed.scheme.lower() not in ("http", "https"):
            raise ValueError(
                f"Invalid URL scheme '{parsed.scheme}'. URL must start with http:// or https://"
            )

        if not parsed.netloc:
            raise ValueError(
                "Invalid URL format: missing domain name (e.g. https://docs.langchain.com)."
            )

    def fetch_and_clean(self) -> Dict[str, Any]:
        """
        Fetch webpage HTML over HTTP, strip unwanted elements (nav, footer, ad, scripts),
        and extract cleaned text and metadata.
        
        Returns:
            dict containing: text, title, metadata, processing_time_ms
        """
        start_time = time.time()
        logger.info(f"[WebLoader] Fetching webpage URL: {self.url}")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            response = requests.get(
                self.url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
        except requests.exceptions.SSLError as ssl_err:
            logger.error(f"[WebLoader] SSL verification failed for {self.url}: {ssl_err}")
            raise RuntimeError(f"SSL certificate verification failed for {self.url}")
        except requests.exceptions.Timeout:
            logger.error(f"[WebLoader] Connection timed out after {self.timeout}s for {self.url}")
            raise RuntimeError(f"Request timed out connecting to {self.url} (limit {self.timeout}s)")
        except requests.exceptions.HTTPError as http_err:
            status_code = response.status_code if 'response' in locals() and response is not None else 404
            logger.error(f"[WebLoader] HTTP error {status_code} for {self.url}: {http_err}")
            if status_code == 404:
                raise RuntimeError(f"Page not found (404 Error) at {self.url}")
            elif status_code in (401, 403):
                raise RuntimeError(f"Access blocked ({status_code} Forbidden/Unauthorized) by {self.url}")
            else:
                raise RuntimeError(f"HTTP Error {status_code} returned by web server")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"[WebLoader] Failed to connect to {self.url}: {req_err}")
            raise RuntimeError(f"Could not connect to URL {self.url}: {str(req_err)}")

        html_content = response.text
        status_code = response.status_code
        content_type = response.headers.get("Content-Type", "text/html")

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract Page Title
        title_tag = soup.find("title")
        page_title = title_tag.get_text().strip() if title_tag else urlparse(self.url).netloc

        # Remove navigation, headers, footers, sidebars, ads, scripts, styles
        unwanted_selectors = [
            "script", "style", "nav", "footer", "header", "aside",
            "noscript", "iframe", "svg", ".nav", ".navbar", ".footer",
            ".header", ".sidebar", ".menu", ".ad", ".advertisement",
            "#nav", "#footer", "#header", "#sidebar", "#menu", "#comments"
        ]
        for element in soup.find_all(unwanted_selectors):
            element.decompose()

        # Extract text from main content container if available, otherwise body
        main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup
        raw_text = main_content.get_text(separator=" ")

        # Clean whitespace and multiline spaces
        lines = (line.strip() for line in raw_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = "\n".join(chunk for chunk in chunks if chunk)

        if not cleaned_text or len(cleaned_text.strip()) < 20:
            raise RuntimeError(f"No readable text content extracted from webpage {self.url}")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[WebLoader] Extracted {len(cleaned_text)} chars from '{page_title}' in {elapsed_ms}ms")

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        metadata = {
            "source_url": self.url,
            "page_title": page_title,
            "timestamp": timestamp,
            "content_type": content_type,
            "status_code": status_code,
            "content_length": len(cleaned_text),
            "processing_time_ms": elapsed_ms
        }

        return {
            "text": cleaned_text,
            "title": page_title,
            "metadata": metadata,
            "processing_time_ms": elapsed_ms
        }

    def load(self) -> List[Document]:
        """
        Load webpage and return list of LangChain Document objects.
        """
        data = self.fetch_and_clean()
        doc = Document(
            page_content=data["text"],
            metadata=data["metadata"]
        )
        return [doc]

