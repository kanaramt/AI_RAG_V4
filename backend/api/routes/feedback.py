from fastapi import APIRouter

from schemas.feedback.knowledge_feedback import (
    KnowledgeFeedback,
)
from services.feedback.feedback_service import (
    FeedbackService,
)

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)

feedback_service = FeedbackService()


@router.post("/")
async def submit_feedback(
    feedback: KnowledgeFeedback,
):
    """
    Submit knowledge feedback and update interaction dataset JSON.
    """
    from services.dataset_service import DatasetService

    success = feedback_service.submit(
        feedback
    )

    # Sync with DatasetService if document_id/chunk_id or interaction_id is present
    target_id = feedback.document_id or feedback.chunk_id or feedback.source
    if target_id:
        DatasetService.update_feedback(target_id, feedback.action)

    return {
        "success": success,
        "message": "Feedback received.",
    }
