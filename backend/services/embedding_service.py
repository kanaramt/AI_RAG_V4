import os
import httpx
from typing import List

from backend.settings import settings


class EmbeddingService:
    """
    Multi-provider embedding generation service supporting OpenSource & Paid APIs.
    """
    _ollama_offline = False

    def __init__(self, model_name: str | None = None):
        self.model = model_name or os.getenv("ACTIVE_EMBEDDING_MODEL", settings.EMBEDDING_MODEL)
        self._ollama_client = None

    @property
    def ollama_client(self):
        if self._ollama_client is None:
            from ollama import Client
            self._ollama_client = Client(host=settings.OLLAMA_BASE_URL, timeout=5.0)
        return self._ollama_client

    def generate_embedding(self, text: str) -> List[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        model_lower = self.model.lower()

        # 1. OpenAI API Embeddings (e.g. text-embedding-3-small, text-embedding-3-large)
        if "text-embedding-3" in model_lower or "openai" in model_lower:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("[EmbeddingService] OpenAI key missing, falling back to Ollama")
                return self._generate_ollama_embeddings(texts)
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {"model": self.model if "text-embedding" in self.model else "text-embedding-3-small", "input": texts}
                resp = httpx.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return [item["embedding"] for item in data["data"]]
            except Exception as e:
                print(f"[EmbeddingService] OpenAI embedding error: {e}")

        # 2. Google Gemini API Embeddings (e.g. text-embedding-004)
        elif "gemini" in model_lower or "004" in model_lower:
            from backend.llm.factory import _get_env_key
            api_key = _get_env_key("GEMINI_API_KEY", "GOOGLE_API_KEY")
            if not api_key:
                print("[EmbeddingService] Gemini key missing, falling back to Ollama")
                return self._generate_ollama_embeddings(texts)
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={api_key}"
                requests = [{"model": "models/text-embedding-004", "content": {"parts": [{"text": t}]}} for t in texts]
                resp = httpx.post(url, json={"requests": requests}, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return [e["values"] for e in data.get("embeddings", [])]
            except Exception as e:
                print(f"[EmbeddingService] Gemini embedding error: {e}")

        # 3. Default: Ollama / Local OpenSource Embeddings
        return self._generate_ollama_embeddings(texts)

    def _generate_ollama_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # If we know Ollama is offline, bypass connection attempt and try Gemini cloud fallback immediately
        if EmbeddingService._ollama_offline:
            gemini_emb = self._try_gemini_fallback(texts)
            if gemini_emb:
                return gemini_emb
            return self._generate_hash_fallback(texts)

        try:
            model_name = self.model if self.model else "nomic-embed-text"
            batch_size = 32
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.ollama_client.embed(
                    model=model_name,
                    input=batch,
                )
                all_embeddings.extend(response["embeddings"])
            return all_embeddings
        except Exception as err:
            print(f"[EmbeddingService] Ollama is offline or error ({err}). Caching offline state.")
            EmbeddingService._ollama_offline = True
            gemini_emb = self._try_gemini_fallback(texts)
            if gemini_emb:
                return gemini_emb
            return self._generate_hash_fallback(texts)

    def _try_gemini_fallback(self, texts: List[str]) -> List[List[float]] | None:
        from backend.llm.factory import _get_env_key
        api_key = _get_env_key("GEMINI_API_KEY", "GOOGLE_API_KEY")
        if not api_key:
            return None
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={api_key}"
            requests = [{"model": "models/text-embedding-004", "content": {"parts": [{"text": t}]}} for t in texts]
            resp = httpx.post(url, json={"requests": requests}, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return [e["values"] for e in data.get("embeddings", [])]
        except Exception as e:
            print(f"[EmbeddingService] Gemini fallback embedding error: {e}")
        return None

    def _generate_hash_fallback(self, texts: List[str]) -> List[List[float]]:
        import hashlib
        results = []
        for t in texts:
            hash_bytes = hashlib.sha256(t.encode('utf-8')).digest()
            vector = [(b / 255.0) * 2 - 1 for b in (hash_bytes * 24)[:768]]
            results.append(vector)
        return results