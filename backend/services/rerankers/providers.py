from typing import List
import os
import requests
from settings import settings
from schemas.retrieval.retrieved_document import RetrievedDocument
from services.rerankers.base import BaseReranker
from core.model_cache import ModelCache

class LocalReranker(BaseReranker):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.RERANKER_MODEL
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = ModelCache.get_cross_encoder(self.model_name)
        return self._model

    def rerank(self, query: str, documents: List[RetrievedDocument], top_k: int = 3) -> List[RetrievedDocument]:
        if not documents:
            return []
        
        sentence_pairs = [(query, document.text) for document in documents]
        scores = self.model.predict(sentence_pairs)
        
        for document, score in zip(documents, scores):
            document.score = float(score)
            
        documents = [doc for doc in documents if doc.score >= 0.3]
        documents.sort(key=lambda document: document.score, reverse=True)
        return documents[:top_k]

class JinaReranker(BaseReranker):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("JINA_API_KEY is required for JinaReranker")
            
    def rerank(self, query: str, documents: List[RetrievedDocument], top_k: int = 3) -> List[RetrievedDocument]:
        if not documents:
            return []
            
        url = "https://api.jina.ai/v1/rerank"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        docs_text = [doc.text for doc in documents]
        data = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query,
            "documents": docs_text,
            "top_n": top_k
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        reranked_docs = []
        for res in results:
            idx = res["index"]
            score = res["relevance_score"]
            doc = documents[idx]
            doc.score = float(score)
            reranked_docs.append(doc)
            
        return reranked_docs[:top_k]

class CohereReranker(BaseReranker):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY is required for CohereReranker")
            
    def rerank(self, query: str, documents: List[RetrievedDocument], top_k: int = 3) -> List[RetrievedDocument]:
        if not documents:
            return []
            
        import cohere
        co = cohere.Client(self.api_key)
        docs_text = [doc.text for doc in documents]
        
        response = co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=docs_text,
            top_n=top_k,
        )
        
        reranked_docs = []
        for res in response.results:
            idx = res.index
            score = res.relevance_score
            doc = documents[idx]
            doc.score = float(score)
            reranked_docs.append(doc)
            
        return reranked_docs[:top_k]
