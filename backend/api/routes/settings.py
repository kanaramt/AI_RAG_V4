import os

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from settings import settings

from services.embeddings.embedding_registry import (
    EMBEDDING_MODEL_MAP,
    DEFAULT_EMBEDDING_MODEL,
    get_embedding_model,
    register_embedding_model,
    persist_to_db,
)

from services.embeddings.huggingface_validator import (
    validate_huggingface_embedding,
)


router = APIRouter()


# ------------------------------------------------------------------
# General API / System Settings Models
# ------------------------------------------------------------------

class APIKeysModel(BaseModel):
    openai_api_key: str | None = ""
    anthropic_api_key: str | None = ""
    gemini_api_key: str | None = ""
    grok_api_key: str | None = ""
    groq_api_key: str | None = ""
    default_cloud_model: str | None = "gpt-4o"


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
    from llm.factory import MODEL_PROVIDER_MAP

    m_lower = (model or "").lower()

    return MODEL_PROVIDER_MAP.get(
        m_lower,
        "ollama",
    )


def _update_env_file(key_values: dict[str, str]):
    """
    Update or append key-value pairs in the .env file.
    """

    env_path = settings.PROJECT_ROOT / ".env"

    lines = []

    if env_path.exists():
        try:
            with open(
                env_path,
                "r",
                encoding="utf-8",
            ) as f:
                lines = f.readlines()

        except Exception as e:
            print(f"[Settings] Error reading .env: {e}")

    updated_keys = set()
    new_lines = []

    for line in lines:
        stripped = line.strip()

        if (
            stripped
            and not stripped.startswith("#")
            and "=" in stripped
        ):
            k, _ = stripped.split("=", 1)
            k = k.strip()

            if k in key_values:
                new_lines.append(
                    f"{k}={key_values[k]}\n"
                )
                updated_keys.add(k)
                continue

        new_lines.append(line)

    for k, v in key_values.items():

        if k not in updated_keys:
            new_lines.append(
                f"{k}={v}\n"
            )

    try:
        with open(
            env_path,
            "w",
            encoding="utf-8",
        ) as f:
            f.writelines(new_lines)

    except Exception as e:
        print(
            f"[Settings] Error writing .env: {e}"
        )


# ------------------------------------------------------------------
# Centralized Settings
# ------------------------------------------------------------------

@router.get("")
@router.get("/")
async def get_centralized_settings():
    """
    Centralized Settings GET endpoint.
    """

    env_file = settings.PROJECT_ROOT / ".env"

    if env_file.exists():
        load_dotenv(
            env_file,
            override=True,
        )

    active_model = (
        os.getenv("DEFAULT_CLOUD_MODEL")
        or os.getenv("LLM_MODEL")
        or os.getenv(
            "CHAT_MODEL",
            settings.DEFAULT_MODEL,
        )
    )

    active_provider = (
        os.getenv("DEFAULT_PROVIDER")
        or os.getenv("LLM_PROVIDER")
        or _infer_provider(active_model)
    )

    openai_k = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

    anthropic_k = os.getenv(
        "ANTHROPIC_API_KEY",
        "",
    )

    gemini_k = (
        os.getenv("GEMINI_API_KEY", "")
        or os.getenv("GOOGLE_API_KEY", "")
    )

    grok_k = (
        os.getenv("GROK_API_KEY", "")
        or os.getenv("XAI_API_KEY", "")
    )

    groq_k = os.getenv(
        "GROQ_API_KEY",
        "",
    )

    def mask(k: str) -> str:

        if not k or len(k) < 6:
            return k

        return (
            k[:4]
            + "..."
            + k[-4:]
        )

    top_k = int(
        os.getenv(
            "RETRIEVER_TOP_K",
            "3",
        )
    )

    similarity = float(
        os.getenv(
            "RETRIEVER_SIMILARITY",
            os.getenv(
                "RETRIEVAL_MIN_SCORE",
                "0.75",
            ),
        )
    )

    min_required_chunks = int(
        os.getenv(
            "MIN_REQUIRED_CHUNKS",
            "2",
        )
    )

    temperature = float(
        os.getenv(
            "LLM_TEMPERATURE",
            "0.2",
        )
    )

    sp_file = (
        settings.PROJECT_ROOT
        / "backend"
        / "data"
        / "system_prompt.txt"
    )

    if sp_file.exists():

        try:
            with open(
                sp_file,
                "r",
                encoding="utf-8",
            ) as f:
                system_prompt = f.read()

        except Exception:
            system_prompt = os.getenv(
                "SYSTEM_PROMPT",
                settings.SYSTEM_PROMPT,
            )

    else:
        system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            settings.SYSTEM_PROMPT,
        )

    return JSONResponse(
        content={
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
                "min_required_chunks": min_required_chunks,
            },

            "system_prompt": system_prompt,
        }
    )


# ------------------------------------------------------------------
# Update Centralized Settings
# ------------------------------------------------------------------

@router.put("")
@router.put("/")
@router.post("")
@router.post("/")
async def update_centralized_settings(
    data: SystemSettingsModel,
):
    """
    Centralized Settings PUT/POST endpoint.
    """

    to_update = {}

    if (
        data.active_model
        and data.active_model.strip()
    ):

        model_val = data.active_model.strip()

        os.environ[
            "DEFAULT_CLOUD_MODEL"
        ] = model_val

        os.environ[
            "LLM_MODEL"
        ] = model_val

        to_update[
            "DEFAULT_CLOUD_MODEL"
        ] = model_val

        to_update[
            "LLM_MODEL"
        ] = model_val

        provider_val = (
            data.active_provider.strip()
            if data.active_provider
            else _infer_provider(model_val)
        )

        os.environ[
            "DEFAULT_PROVIDER"
        ] = provider_val

        os.environ[
            "LLM_PROVIDER"
        ] = provider_val

        to_update[
            "DEFAULT_PROVIDER"
        ] = provider_val

        to_update[
            "LLM_PROVIDER"
        ] = provider_val

    if (
        data.openai_api_key is not None
        and data.openai_api_key.strip()
    ):

        val = data.openai_api_key.strip()

        os.environ[
            "OPENAI_API_KEY"
        ] = val

        to_update[
            "OPENAI_API_KEY"
        ] = val

    if (
        data.anthropic_api_key is not None
        and data.anthropic_api_key.strip()
    ):

        val = data.anthropic_api_key.strip()

        os.environ[
            "ANTHROPIC_API_KEY"
        ] = val

        to_update[
            "ANTHROPIC_API_KEY"
        ] = val

    if (
        data.gemini_api_key is not None
        and data.gemini_api_key.strip()
    ):

        val = data.gemini_api_key.strip()

        os.environ[
            "GEMINI_API_KEY"
        ] = val

        os.environ[
            "GOOGLE_API_KEY"
        ] = val

        to_update[
            "GEMINI_API_KEY"
        ] = val

        to_update[
            "GOOGLE_API_KEY"
        ] = val

    if (
        data.grok_api_key is not None
        and data.grok_api_key.strip()
    ):

        val = data.grok_api_key.strip()

        os.environ[
            "GROK_API_KEY"
        ] = val

        os.environ[
            "XAI_API_KEY"
        ] = val

        to_update[
            "GROK_API_KEY"
        ] = val

        to_update[
            "XAI_API_KEY"
        ] = val

    if (
        data.groq_api_key is not None
        and data.groq_api_key.strip()
    ):

        val = data.groq_api_key.strip()

        os.environ[
            "GROQ_API_KEY"
        ] = val

        to_update[
            "GROQ_API_KEY"
        ] = val

    if data.top_k is not None:

        os.environ[
            "RETRIEVER_TOP_K"
        ] = str(data.top_k)

        to_update[
            "RETRIEVER_TOP_K"
        ] = str(data.top_k)

    if data.similarity is not None:

        os.environ[
            "RETRIEVER_SIMILARITY"
        ] = str(data.similarity)

        os.environ[
            "RETRIEVAL_MIN_SCORE"
        ] = str(data.similarity)

        to_update[
            "RETRIEVER_SIMILARITY"
        ] = str(data.similarity)

        to_update[
            "RETRIEVAL_MIN_SCORE"
        ] = str(data.similarity)

    if data.retrieval_min_score is not None:

        os.environ[
            "RETRIEVAL_MIN_SCORE"
        ] = str(
            data.retrieval_min_score
        )

        os.environ[
            "RETRIEVER_SIMILARITY"
        ] = str(
            data.retrieval_min_score
        )

        to_update[
            "RETRIEVAL_MIN_SCORE"
        ] = str(
            data.retrieval_min_score
        )

        to_update[
            "RETRIEVER_SIMILARITY"
        ] = str(
            data.retrieval_min_score
        )

    if data.min_required_chunks is not None:

        os.environ[
            "MIN_REQUIRED_CHUNKS"
        ] = str(
            data.min_required_chunks
        )

        to_update[
            "MIN_REQUIRED_CHUNKS"
        ] = str(
            data.min_required_chunks
        )

    if data.temperature is not None:

        os.environ[
            "LLM_TEMPERATURE"
        ] = str(
            data.temperature
        )

        to_update[
            "LLM_TEMPERATURE"
        ] = str(
            data.temperature
        )

    if data.system_prompt is not None:

        sp_file = (
            settings.PROJECT_ROOT
            / "backend"
            / "data"
            / "system_prompt.txt"
        )

        sp_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            with open(
                sp_file,
                "w",
                encoding="utf-8",
            ) as f:

                f.write(
                    data.system_prompt
                )

        except Exception as e:

            print(
                "[Settings] Error writing "
                f"system_prompt.txt: {e}"
            )

        os.environ[
            "SYSTEM_PROMPT"
        ] = data.system_prompt

        sanitized_prompt = (
            data.system_prompt
            .replace("\n", " ")
            .replace("\r", "")
        )

        to_update[
            "SYSTEM_PROMPT"
        ] = sanitized_prompt

    if to_update:
        _update_env_file(to_update)

    return await get_centralized_settings()


# ------------------------------------------------------------------
# API Keys
# ------------------------------------------------------------------

@router.get("/keys")
async def get_api_keys():
    return await get_centralized_settings()


@router.post("/keys")
async def save_api_keys(
    data: APIKeysModel,
):

    settings_data = SystemSettingsModel(
        active_model=data.default_cloud_model,
        openai_api_key=data.openai_api_key,
        anthropic_api_key=data.anthropic_api_key,
        gemini_api_key=data.gemini_api_key,
        grok_api_key=data.grok_api_key,
        groq_api_key=data.groq_api_key,
    )

    return await update_centralized_settings(
        settings_data
    )


# ------------------------------------------------------------------
# Embedding Models
# ------------------------------------------------------------------

class SelectEmbeddingModel(BaseModel):
    model_id: str
    api_key: str | None = None


class ValidateEmbeddingModel(BaseModel):
    model_id: str
    api_key: str | None = None


class AddEmbeddingModel(BaseModel):
    name: str
    provider: str | None = None
    type: str | None = None
    api_key: str | None = None


@router.get("/embeddings")
async def get_embedding_models():

    active = os.getenv(
        "ACTIVE_EMBEDDING_MODEL",
        DEFAULT_EMBEDDING_MODEL,
    )

    models = []

    for model_id, config in EMBEDDING_MODEL_MAP.items():

        models.append(
            {
                "id": model_id,
                "name": config["name"],
                "provider": config["provider"],
                "billing": config["billing"],
                "requires_api_key": config[
                    "requires_api_key"
                ],
                "dims": config["dimension"],
                "desc": config["description"],
            }
        )

    return JSONResponse(
        content={
            "active_model": active,
            "models": models,
        }
    )


@router.post("/embeddings/validate")
async def validate_embedding_model(
    data: ValidateEmbeddingModel,
):

    model_id = data.model_id.strip()

    try:
        model_config = get_embedding_model(
            model_id
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported embedding model: "
                f"{model_id}"
            ),
        )

    if (
        model_config["provider"]
        != "huggingface_hosted"
    ):

        return JSONResponse(
            content={
                "valid": True,
                "model_id": model_id,
                "provider": model_config[
                    "provider"
                ],
                "billing": model_config[
                    "billing"
                ],
                "dimension": model_config[
                    "dimension"
                ],
                "requires_api_key": model_config[
                    "requires_api_key"
                ],
                "message": (
                    "Hosted Hugging Face validation "
                    "is not required for this model."
                ),
            }
        )

    result = validate_huggingface_embedding(
        model_id=model_config.get(
            "model_id",
            model_id,
        ),
        token=data.api_key,
    )

    return JSONResponse(
        content=result
    )


@router.post("/embeddings/select")
async def select_embedding_model(
    data: SelectEmbeddingModel,
):

    model_id = data.model_id.strip()

    try:

        model = get_embedding_model(
            model_id
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported embedding model: "
                f"{model_id}"
            ),
        )

    # For cloud providers: store the api_key in os.environ (request-scoped only,
    # NOT written to .env) so the active EmbeddingService can pick it up.
    if model["requires_api_key"] and data.api_key:
        provider = model["provider"]
        if provider == "openai":
            # Only set if it wasn't already set (prefer server-side key)
            if not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = data.api_key
        elif provider == "gemini":
            if not os.environ.get("GEMINI_API_KEY"):
                os.environ["GEMINI_API_KEY"] = data.api_key
        elif provider == "huggingface_hosted":
            if not os.environ.get("HF_TOKEN"):
                os.environ["HF_TOKEN"] = data.api_key
    elif model["requires_api_key"] and not data.api_key:
        # Cloud model selected but no key provided — check server env
        provider = model["provider"]
        key_present = False
        if provider == "openai" and os.environ.get("OPENAI_API_KEY"):
            key_present = True
        elif provider == "gemini" and (
            os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        ):
            key_present = True
        elif provider == "huggingface_hosted" and (
            os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        ):
            key_present = True
        if not key_present:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Embedding model '{model_id}' requires an API key. "
                    "Please provide it in the request or configure it in Settings."
                ),
            )

    os.environ[
        "ACTIVE_EMBEDDING_MODEL"
    ] = model_id

    _update_env_file(
        {
            "ACTIVE_EMBEDDING_MODEL": model_id
        }
    )

    return JSONResponse(
        content={
            "status": "success",
            "active_model": model_id,
            "provider": model["provider"],
            "billing": model["billing"],
            "dimension": model["dimension"],
            "requires_api_key": model["requires_api_key"],
        }
    )


@router.post("/embeddings/add")
async def add_embedding_model(
    data: AddEmbeddingModel,
):

    model_id = data.name.strip()

    if not model_id:

        raise HTTPException(
            status_code=400,
            detail="Model ID is required.",
        )

    provider = (
        (data.provider or "")
        .strip()
        .lower()
    )

    # --------------------------------------------------------------
    # Hugging Face Hosted
    # --------------------------------------------------------------

    if provider in {
        "huggingface",
        "huggingface hosted",
        "huggingface_hosted",
        "hf",
    }:

        if not data.api_key:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Hugging Face token is required "
                    "for hosted embedding models."
                ),
            )

        validation = validate_huggingface_embedding(
            model_id=model_id,
            token=data.api_key,
        )

        if not validation.get("valid"):
            raise HTTPException(
                status_code=400,
                detail=validation.get(
                    "error",
                    "Hugging Face model validation failed.",
                ),
            )

        dimension = validation.get(
            "dimension"
        )

        if not dimension:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Hugging Face embedding dimension "
                    "could not be detected."
                ),
            )

        _hf_config = {
            "name": model_id,
            "model_id": model_id,
            "provider": "huggingface_hosted",
            "billing": "free_quota",
            "requires_api_key": True,
            "dimension": dimension,
            "description": (
                "Dynamically validated Hugging Face "
                "hosted embedding model."
            ),
        }

        register_embedding_model(model_id, _hf_config)
        persist_to_db(model_id, _hf_config)

        os.environ[
            "ACTIVE_EMBEDDING_MODEL"
        ] = model_id

        _update_env_file(
            {
                "ACTIVE_EMBEDDING_MODEL": model_id
            }
        )

        return JSONResponse(
            content={
                "status": "success",
                "message": (
                    f"Hugging Face embedding model "
                    f"'{model_id}' validated, "
                    "registered and activated."
                ),
                "model": {
                    "id": model_id,
                    "name": model_id,
                    "provider": "huggingface_hosted",
                    "billing": "free_quota",
                    "requires_api_key": True,
                    "dimension": dimension,
                },
            }
        )

    # --------------------------------------------------------------
    # Existing registered models
    # --------------------------------------------------------------

    if model_id in EMBEDDING_MODEL_MAP:

        model = get_embedding_model(
            model_id
        )

        if (
            model["requires_api_key"]
            and not data.api_key
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"API key is required for "
                    f"embedding model '{model_id}'."
                ),
            )

        os.environ[
            "ACTIVE_EMBEDDING_MODEL"
        ] = model_id

        _update_env_file(
            {
                "ACTIVE_EMBEDDING_MODEL": model_id
            }
        )

        return JSONResponse(
            content={
                "status": "success",
                "message": (
                    f"Embedding model "
                    f"'{model_id}' activated."
                ),
                "model": {
                    "id": model_id,
                    "name": model["name"],
                    "provider": model[
                        "provider"
                    ],
                    "billing": model[
                        "billing"
                    ],
                    "dimension": model[
                        "dimension"
                    ],
                    "requires_api_key": model[
                        "requires_api_key"
                    ],
                },
            }
        )

    # --------------------------------------------------------------
    # Unsupported custom provider
    # --------------------------------------------------------------

    raise HTTPException(
        status_code=400,
        detail=(
            "Unsupported provider. "
            "Use a registered model or "
            "Hugging Face hosted."
        ),
    )