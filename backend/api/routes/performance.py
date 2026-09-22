from fastapi import APIRouter, Depends
from dependencies import get_memory
from services.vector_store.factory import VectorStoreFactory

router = APIRouter()

@router.get("/stats")
async def get_performance_stats(memory = Depends(get_memory)):
    """
    Aggegrates and logs performance metrics (relevance, faithfulness, latency)
    as well as document chunk distribution stats.
    """
    # 1. Fetch document list from SQLite
    docs = memory.list_documents()
    documents_list = []
    for doc in docs:
        documents_list.append({
            'filename': doc['name'],
            'type': doc['type']
        })
        
    # 2. Fetch total chunk points from Qdrant
    total_chunks = 0
    try:
        vector_store = VectorStoreFactory.create()
        qdrant = vector_store.qdrant
        info = qdrant.client.get_collection(qdrant.collection_name)
        total_chunks = info.points_count
    except Exception as e:
        print(f"Error retrieving collection details from Qdrant: {e}")

    # 3. Fetch RAG evaluation stats from SQLite
    evals = memory.get_eval_stats()

    return {
        "total_chunks": total_chunks,
        "total_files": len(documents_list),
        "documents": documents_list,
        "historical": evals["historical"],
        "current": evals["current"]
    }
