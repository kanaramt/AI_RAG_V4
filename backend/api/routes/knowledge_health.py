from fastapi import APIRouter

from services.health.knowledge_health_service import (
    KnowledgeHealthService,
)

router = APIRouter(
    prefix="/knowledge-health",
    tags=["Knowledge Health"],
)

health_service = KnowledgeHealthService()


@router.get("/")
async def get_knowledge_health():
    """
    Returns the overall health of the enterprise knowledge base.
    """

    return health_service.calculate()
