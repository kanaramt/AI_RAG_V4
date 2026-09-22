import os
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from settings import settings

router = APIRouter()

class APIKeysModel(BaseModel):
    openai_api_key: str | None = ""
    anthropic_api_key: str | None = ""
    gemini_api_key: str | None = ""
    grok_api_key: str | None = ""
    groq_api_key: str | None = ""
    default_cloud_model: str | None = "gemini-2.5-flash"


class SystemSettingsModel(BaseModel):
    active_provider: str | None = None
    active_model: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    grok_api_key: str | None = None
    groq_api_key: str | None = None
    top_k: int | None = None
    similarity: float | None = None
    temperature: float | None = None
    system_prompt: str | None = None
    retrieval_min_score: float | None = None
    min_required_chunks: int | None = None



def _infer_provider(model: str) -> str:
    m_lower = (model or "").lower()
    if any(k in m_lower for k in ["gemini", "flash", "pro-latest"]):
        return "gemini"
    elif any(k in m_lower for k in ["llama-3", "mixtral", "gemma", "versatile", "instant", "groq"]):
        return "groq"
    elif any(k in m_lower for k in ["gpt-4", "gpt-3", "openai"]):
        return "openai"
    elif any(k in m_lower for k in ["claude", "anthropic"]):
        return "anthropic"
    elif any(k in m_lower for k in ["grok"]):
        return "grok"
    else:
        return "ollama"


def _update_env_file(key_values: dict[str, str]):
    """
    Update or append key-value pairs in the .env file.
    """
    env_path = settings.PROJECT_ROOT / ".env"
    lines = []
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"[Settings] Error reading .env: {e}")

    updated_keys = set()
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, v = stripped.split("=", 1)
            k = k.strip()
            if k in key_values:
                new_lines.append(f"{k}={key_values[k]}\n")
                updated_keys.add(k)
                continue
        new_lines.append(line)

    for k, v in key_values.items():
        if k not in updated_keys:
            new_lines.append(f"{k}={v}\n")

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"[Settings] Error writing .env: {e}")


from dotenv import load_dotenv


@router.get("")
@router.get("/")
async def get_centralized_settings():
    """
    Centralized Settings Single Source of Truth GET endpoint.
    Returns current active provider, active model, API keys, parameters, and system prompt.
    """
    env_file = settings.PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)

    active_model = os.getenv("DEFAULT_CLOUD_MODEL") or os.getenv("LLM_MODEL") or os.getenv("CHAT_MODEL", "gemini-2.5-flash")
    active_provider = os.getenv("DEFAULT_PROVIDER") or os.getenv("LLM_PROVIDER") or _infer_provider(active_model)

    openai_k = os.getenv("OPENAI_API_KEY", "")
    anthropic_k = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_k = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    grok_k = os.getenv("GROK_API_KEY", "") or os.getenv("XAI_API_KEY", "")
    groq_k = os.getenv("GROQ_API_KEY", "")

    def mask(k: str) -> str:
        if not k or len(k) < 6:
            return k
        return k[:4] + "..." + k[-4:]

    top_k = int(os.getenv("RETRIEVER_TOP_K", "3"))
    similarity = float(os.getenv("RETRIEVER_SIMILARITY", os.getenv("RETRIEVAL_MIN_SCORE", "0.75")))
    min_required_chunks = int(os.getenv("MIN_REQUIRED_CHUNKS", "2"))
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    # Load system prompt from file if present to support max length and multiline without corrupting .env
    sp_file = settings.PROJECT_ROOT / "backend" / "data" / "system_prompt.txt"
    if sp_file.exists():
        try:
            with open(sp_file, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except Exception:
            system_prompt = os.getenv("SYSTEM_PROMPT", settings.SYSTEM_PROMPT)
    else:
        system_prompt = os.getenv("SYSTEM_PROMPT", settings.SYSTEM_PROMPT)

    return JSONResponse(content={
        "status": "success",
        "active_provider": active_provider,
        "active_model": active_model,
        "api_keys": {
            "openai_api_key": openai_k,
            "anthropic_api_key": anthropic_k,
            "gemini_api_key": gemini_k,
            "grok_api_key": grok_k,
            "groq_api_key": groq_k,
        },
        "masked_keys": {
            "openai_masked": mask(openai_k),
            "anthropic_masked": mask(anthropic_k),
            "gemini_masked": mask(gemini_k),
            "grok_masked": mask(grok_k),
            "groq_masked": mask(groq_k),
        },
        "retriever_params": {
            "topK": top_k,
            "similarity": similarity,
            "temperature": temperature,
            "retrieval_min_score": similarity,
            "min_required_chunks": min_required_chunks
        },
        "system_prompt": system_prompt
    })



@router.put("")
@router.put("/")
@router.post("")
@router.post("/")
async def update_centralized_settings(data: SystemSettingsModel):
    """
    Centralized Settings PUT/POST endpoint.
    Updates active provider, model, keys, retriever parameters, and system prompt.
    Persists changes dynamically in os.environ and .env file.
    """
    to_update = {}

    if data.active_model and data.active_model.strip():
        model_val = data.active_model.strip()
        os.environ["DEFAULT_CLOUD_MODEL"] = model_val
        os.environ["LLM_MODEL"] = model_val
        to_update["DEFAULT_CLOUD_MODEL"] = model_val
        to_update["LLM_MODEL"] = model_val

        provider_val = data.active_provider.strip() if data.active_provider else _infer_provider(model_val)
        os.environ["DEFAULT_PROVIDER"] = provider_val
        os.environ["LLM_PROVIDER"] = provider_val
        to_update["DEFAULT_PROVIDER"] = provider_val
        to_update["LLM_PROVIDER"] = provider_val

    if data.openai_api_key is not None and data.openai_api_key.strip():
        val = data.openai_api_key.strip()
        os.environ["OPENAI_API_KEY"] = val
        to_update["OPENAI_API_KEY"] = val

    if data.anthropic_api_key is not None and data.anthropic_api_key.strip():
        val = data.anthropic_api_key.strip()
        os.environ["ANTHROPIC_API_KEY"] = val
        to_update["ANTHROPIC_API_KEY"] = val

    if data.gemini_api_key is not None and data.gemini_api_key.strip():
        val = data.gemini_api_key.strip()
        os.environ["GEMINI_API_KEY"] = val
        os.environ["GOOGLE_API_KEY"] = val
        to_update["GEMINI_API_KEY"] = val
        to_update["GOOGLE_API_KEY"] = val

    if data.grok_api_key is not None and data.grok_api_key.strip():
        val = data.grok_api_key.strip()
        os.environ["GROK_API_KEY"] = val
        os.environ["XAI_API_KEY"] = val
        to_update["GROK_API_KEY"] = val
        to_update["XAI_API_KEY"] = val

    if data.groq_api_key is not None and data.groq_api_key.strip():
        val = data.groq_api_key.strip()
        os.environ["GROQ_API_KEY"] = val
        to_update["GROQ_API_KEY"] = val

    if data.top_k is not None:
        os.environ["RETRIEVER_TOP_K"] = str(data.top_k)
        to_update["RETRIEVER_TOP_K"] = str(data.top_k)

    if data.similarity is not None:
        os.environ["RETRIEVER_SIMILARITY"] = str(data.similarity)
        to_update["RETRIEVER_SIMILARITY"] = str(data.similarity)
        os.environ["RETRIEVAL_MIN_SCORE"] = str(data.similarity)
        to_update["RETRIEVAL_MIN_SCORE"] = str(data.similarity)

    if data.retrieval_min_score is not None:
        os.environ["RETRIEVAL_MIN_SCORE"] = str(data.retrieval_min_score)
        to_update["RETRIEVAL_MIN_SCORE"] = str(data.retrieval_min_score)
        os.environ["RETRIEVER_SIMILARITY"] = str(data.retrieval_min_score)
        to_update["RETRIEVER_SIMILARITY"] = str(data.retrieval_min_score)

    if data.min_required_chunks is not None:
        os.environ["MIN_REQUIRED_CHUNKS"] = str(data.min_required_chunks)
        to_update["MIN_REQUIRED_CHUNKS"] = str(data.min_required_chunks)

    if data.temperature is not None:
        os.environ["LLM_TEMPERATURE"] = str(data.temperature)
        to_update["LLM_TEMPERATURE"] = str(data.temperature)

    if data.system_prompt is not None:
        # Save exact prompt (with newlines/large text) to flat file
        sp_file = settings.PROJECT_ROOT / "backend" / "data" / "system_prompt.txt"
        sp_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(sp_file, "w", encoding="utf-8") as f:
                f.write(data.system_prompt)
        except Exception as e:
            print(f"[Settings] Error writing system_prompt.txt: {e}")
            
        os.environ["SYSTEM_PROMPT"] = data.system_prompt
        # Sanitize for .env file (remove newlines to prevent parsing errors)
        sanitized_prompt = data.system_prompt.replace("\n", " ").replace("\r", "")
        to_update["SYSTEM_PROMPT"] = sanitized_prompt

    if to_update:
        _update_env_file(to_update)

    return await get_centralized_settings()


@router.get("/keys")
async def get_api_keys():
    """
    Get currently configured API keys (masked) and default cloud model.
    """
    return await get_centralized_settings()


@router.post("/keys")
async def save_api_keys(data: APIKeysModel):
    """
    Save API keys and default cloud model dynamically in os.environ and persist to .env.
    """
    settings_data = SystemSettingsModel(
        active_model=data.default_cloud_model,
        openai_api_key=data.openai_api_key,
        anthropic_api_key=data.anthropic_api_key,
        gemini_api_key=data.gemini_api_key,
        grok_api_key=data.grok_api_key,
        groq_api_key=data.groq_api_key,
    )
    return await update_centralized_settings(settings_data)


# ------------------------------------------------------------------
# Embedding Models Management Endpoints (OpenSource vs Paid)
# ------------------------------------------------------------------

DEFAULT_EMBEDDING_MODELS = [
    {
        "id": "nomic-embed-text",
        "name": "nomic-embed-text",
        "type": "opensource",
        "provider": "Ollama / Local Server",
        "desc": "High accuracy 768-dimensional local vector embedding model.",
        "dims": 768
    },
    {
        "id": "BAAI/bge-small-en-v1.5",
        "name": "BAAI/bge-small-en-v1.5",
        "type": "opensource",
        "provider": "HuggingFace Local",
        "desc": "Top-ranked 384-dimensional lightweight local open-source embedding.",
        "dims": 384
    },
    {
        "id": "text-embedding-3-small",
        "name": "text-embedding-3-small",
        "type": "paid",
        "provider": "OpenAI Cloud API",
        "desc": "OpenAI 1536-dimensional highly efficient cloud embedding API.",
        "dims": 1536
    },
    {
        "id": "text-embedding-004",
        "name": "text-embedding-004",
        "type": "paid",
        "provider": "Google Gemini API",
        "desc": "Google Gemini 768-dimensional state-of-the-art cloud embedding API.",
        "dims": 768
    }
]

CUSTOM_EMBEDDING_MODELS = []


class SelectEmbeddingModel(BaseModel):
    model_id: str


class AddEmbeddingModel(BaseModel):
    name: str
    type: str  # "opensource" or "paid"
    provider: str
    api_key: str | None = ""


@router.get("/embeddings")
async def get_embedding_models():
    active = os.getenv("ACTIVE_EMBEDDING_MODEL", "nomic-embed-text")
    all_models = DEFAULT_EMBEDDING_MODELS + CUSTOM_EMBEDDING_MODELS
    return JSONResponse(content={
        "active_model": active,
        "models": all_models
    })


@router.post("/embeddings/select")
async def select_embedding_model(data: SelectEmbeddingModel):
    os.environ["ACTIVE_EMBEDDING_MODEL"] = data.model_id
    _update_env_file({"ACTIVE_EMBEDDING_MODEL": data.model_id})
    return JSONResponse(content={"status": "success", "message": f"Active embedding model changed to {data.model_id}"})


@router.post("/embeddings/add")
async def add_embedding_model(data: AddEmbeddingModel):
    new_id = data.name.strip()
    if not new_id:
        raise HTTPException(status_code=400, detail="Model name is required.")
    
    new_model = {
        "id": new_id,
        "name": new_id,
        "type": data.type.lower(),
        "provider": data.provider,
        "desc": f"Custom registered {data.type} model on {data.provider}.",
        "dims": 768
    }
    
    if not any(m["id"] == new_id for m in DEFAULT_EMBEDDING_MODELS + CUSTOM_EMBEDDING_MODELS):
        CUSTOM_EMBEDDING_MODELS.append(new_model)
        
    os.environ["ACTIVE_EMBEDDING_MODEL"] = new_id
    _update_env_file({"ACTIVE_EMBEDDING_MODEL": new_id})
    
    return JSONResponse(content={
        "status": "success",
        "message": f"Successfully registered and activated embedding model '{new_id}'!",
        "model": new_model
    })
