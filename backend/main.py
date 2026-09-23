import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env into os.environ on startup
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

# Force PyTorch and OpenMP to run on a single thread to prevent segmentation faults/crashes in Uvicorn
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Lazy PyTorch thread limit set without importing heavy torch at startup
try:
    if "torch" in sys.modules:
        sys.modules["torch"].set_num_threads(1)
except Exception:
    pass

#from lifespan import lifespan
from lifespan import lifespan

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#from settings import settings
#from api.router import api_router
from settings import settings
from api.router import api_router



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Restrict later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app.include_router(api_router, prefix="/api")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Serve Frontend static assets
#app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
#app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

@app.get("/")
async def read_root():
    return FileResponse(
        str(FRONTEND_DIR / "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )

@app.get("/style.css")
async def read_style():
    return FileResponse(str(FRONTEND_DIR / "style.css"))

@app.get("/app.js")
async def read_app_js():
    return FileResponse(str(FRONTEND_DIR / "app.js"))

@app.get("/performance")
async def read_performance():
    return FileResponse(
        str(FRONTEND_DIR / "performance.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )

@app.get("/dataset")
async def read_dataset():
    return FileResponse(
        str(FRONTEND_DIR / "dataset.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@app.get("/website")
async def read_website():
    return FileResponse(
        str(FRONTEND_DIR / "website.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
