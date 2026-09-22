from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from services.dataset_service import DatasetService

router = APIRouter()


class FeedbackUpdateSchema(BaseModel):
    interaction_id: str
    feedback: str

@router.get("/stats")
async def get_dataset_stats():
    """
    Returns dataset statistics (total queries, positive feedback, negative feedback, total disk size).
    """
    return DatasetService.get_stats()

@router.get("/queries")
async def get_dataset_queries(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    feedback_type: Optional[str] = Query("all", description="all | positive | negative | unrated"),
    conversation_id: Optional[str] = Query(None, description="Filter by conversation ID")
):
    """
    Retrieves filtered interaction queries dataset.
    """
    records = DatasetService.get_queries(
        start_date=start_date,
        end_date=end_date,
        feedback_type=feedback_type,
        conversation_id=conversation_id
    )
    return {"count": len(records), "records": records}

@router.get("/export")
async def export_dataset(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    feedback_type: Optional[str] = Query("all"),
    conversation_id: Optional[str] = Query(None)
):
    """
    Exports filtered dataset as JSON file payload.
    """
    records = DatasetService.get_queries(
        start_date=start_date,
        end_date=end_date,
        feedback_type=feedback_type,
        conversation_id=conversation_id
    )
    return JSONResponse(
        content=records,
        headers={"Content-Disposition": "attachment; filename=rag_query_dataset.json"}
    )

@router.post("/feedback")
async def update_interaction_feedback(payload: FeedbackUpdateSchema):
    """
    Updates feedback (positive/negative) for a specific recorded interaction.
    """
    success = DatasetService.update_feedback(payload.interaction_id, payload.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction record not found.")
    return {"status": "success", "message": f"Updated feedback to {payload.feedback}"}

