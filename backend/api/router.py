from fastapi import APIRouter

from api.routes.chat import router as chat_router, history_router
from api.routes.documents import router as documents_router
from api.routes.documents import paste_content, index_url
from api.routes.health import router as health_router
from api.routes.feedback import router as feedback_router
from api.routes.review import router as review_router
from api.routes.evaluation import router as evaluation_router
from api.routes.recommendation import router as recommendation_router
from api.routes.knowledge_health import (
    router as knowledge_health_router,
)
from api.routes.jobs import (
    router as jobs_router,
)
from api.routes.versioning import (
    router as versioning_router,
)
from api.routes.governance import (
    router as governance_router,
)
from api.routes.database import (
    router as database_router,
)
from catalog.api import (
    router as catalog_router,
)
from api.routes.performance import router as performance_router
from api.routes.search import router as search_router
from api.routes.settings import router as settings_router
from api.routes.dataset import router as dataset_router
from api.routes.website_ingestion import router as website_router
from api.routes.document_export import (
    router as export_router,
)
from api.routes.ingestion_history import (
    router as ingestion_history_router,
)

from api.routes.document_catalog import (
    router as document_catalog_router,
)
from api.routes.chunk_catalog import (
    router as chunk_catalog_router,
)

api_router = APIRouter()

api_router.include_router(
    website_router,
    prefix="/website",
    tags=["Website Ingestion"],
)

api_router.include_router(
    dataset_router,
    prefix="/dataset",
    tags=["Dataset Management"],
)



api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    history_router,
)

api_router.include_router(
    chat_router,
    prefix="/chats",  # Plural chats prefix matching frontend
    tags=["Chat"],
)

api_router.include_router(
    documents_router,
    prefix="/documents",
    tags=["Documents"],
)

api_router.include_router(
    search_router,
    tags=["Search"],
)

# Root level endpoints mapping old API contracts
api_router.post("/paste", tags=["Documents"])(paste_content)
api_router.post("/url", tags=["Documents"])(index_url)

api_router.include_router(
    settings_router,
    prefix="/settings",
    tags=["Settings"],
)

api_router.include_router(
    performance_router,
    prefix="/performance",
    tags=["Performance"],
)

api_router.include_router(
    feedback_router,
    tags=["Feedback"],
)

api_router.include_router(
    review_router,
    tags=["Knowledge Review"],
)

api_router.include_router(
    evaluation_router,
    tags=["Evaluation"],
)

api_router.include_router(
    recommendation_router,
    tags=["Recommendation"],
)

api_router.include_router(
    knowledge_health_router,
    tags=["Knowledge Health"],
)

api_router.include_router(
    jobs_router,
    tags=["Jobs"],
)

api_router.include_router(
    versioning_router,
    tags=["Versioning"],
)

api_router.include_router(
    governance_router,
    tags=["Governance"],
)

api_router.include_router(
    database_router,
    tags=["Database"],
)

api_router.include_router(
    catalog_router,
)

api_router.include_router(
    export_router
)

api_router.include_router(
    ingestion_history_router,
)

api_router.include_router(
    document_catalog_router,
)

api_router.include_router(
    chunk_catalog_router,
)
