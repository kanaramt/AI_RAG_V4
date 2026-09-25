"""
Embedding Model Registry.

EMBEDDING_MODEL_MAP is the in-process registry.
Dynamic registrations are persisted to the database (via persist_to_db / load_from_db).
API keys are NEVER stored here.
"""

EMBEDDING_MODEL_MAP: dict[str, dict] = {
    # ------------------------------------------------------------------
    # Ollama Local
    # ------------------------------------------------------------------
    "nomic-embed-text": {
        "name": "nomic-embed-text",
        "provider": "ollama",
        "billing": "free_local",
        "requires_api_key": False,
        "dimension": 768,
        "description": "Local open-source embedding model via Ollama.",
    },
    # ------------------------------------------------------------------
    # HuggingFace Local (SentenceTransformers)
    # ------------------------------------------------------------------
    "BAAI/bge-small-en-v1.5": {
        "name": "BAAI/bge-small-en-v1.5",
        "provider": "huggingface_local",
        "billing": "free_local",
        "requires_api_key": False,
        "dimension": 384,
        "description": "Local open-source BGE embedding model via SentenceTransformers.",
    },
    # ------------------------------------------------------------------
    # OpenAI (paid, request-scoped key)
    # ------------------------------------------------------------------
    "text-embedding-3-small": {
        "name": "text-embedding-3-small",
        "provider": "openai",
        "billing": "paid",
        "requires_api_key": True,
        "dimension": 1536,
        "description": "OpenAI text-embedding-3-small (1536-dim). Requires OPENAI_API_KEY.",
    },
    "text-embedding-3-large": {
        "name": "text-embedding-3-large",
        "provider": "openai",
        "billing": "paid",
        "requires_api_key": True,
        "dimension": 3072,
        "description": "OpenAI text-embedding-3-large (3072-dim). Requires OPENAI_API_KEY.",
    },
    # ------------------------------------------------------------------
    # Google Gemini (paid, request-scoped key)
    # ------------------------------------------------------------------
    "gemini-embedding-2": {
        "name": "gemini-embedding-2",
        "provider": "gemini",
        "billing": "paid",
        "requires_api_key": True,
        "dimension": 3072,
        "description": "Google Gemini Embedding 2 (3072-dim). Requires GEMINI_API_KEY.",
    },
    # ------------------------------------------------------------------
    # Hugging Face Hosted (free_quota tier, requires HF_TOKEN)
    # ------------------------------------------------------------------
    "hf:BAAI/bge-small-en-v1.5": {
        "name": "BAAI/bge-small-en-v1.5",
        "model_id": "BAAI/bge-small-en-v1.5",
        "provider": "huggingface_hosted",
        "billing": "free_quota",
        "requires_api_key": True,
        "dimension": 384,
        "description": "Hugging Face hosted BGE-small (384-dim). Requires HF_TOKEN.",
    },
}

#DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding_model(model_id: str) -> dict:
    """Return registry config for model_id or raise ValueError."""
    model = EMBEDDING_MODEL_MAP.get(model_id)
    if not model:
        raise ValueError(
            f"Unsupported embedding model: '{model_id}'. "
            f"Supported: {list(EMBEDDING_MODEL_MAP.keys())}"
        )
    return model


def is_supported_embedding_model(model_id: str) -> bool:
    return model_id in EMBEDDING_MODEL_MAP


def register_embedding_model(model_id: str, config: dict) -> None:
    """
    Register or update an embedding model at runtime.

    API keys must NOT be included in config.
    """
    EMBEDDING_MODEL_MAP[model_id] = {
        "name": config["name"],
        "provider": config["provider"],
        "billing": config["billing"],
        "requires_api_key": config["requires_api_key"],
        "dimension": config["dimension"],
        "description": config.get("description", ""),
        **(
            {"model_id": config["model_id"]}
            if "model_id" in config
            else {}
        ),
    }


def persist_to_db(model_id: str, config: dict) -> None:
    """
    Persist a dynamic embedding model registration to the database.
    Called after register_embedding_model() for any model that was
    added at runtime so it survives process restarts.

    API keys are never written.
    """
    try:
        from database.session import SessionLocal
        from database.models.embedding_config_model import EmbeddingConfigModel

        db = SessionLocal()
        try:
            existing = db.query(EmbeddingConfigModel).filter(
                EmbeddingConfigModel.model_id == model_id
            ).first()

            if existing:
                existing.name = config["name"]
                existing.provider = config["provider"]
                existing.billing = config["billing"]
                existing.requires_api_key = config["requires_api_key"]
                existing.dimension = config["dimension"]
                existing.description = config.get("description", "")
                existing.underlying_model_id = config.get("model_id")
            else:
                db.add(EmbeddingConfigModel(
                    model_id=model_id,
                    name=config["name"],
                    provider=config["provider"],
                    billing=config["billing"],
                    requires_api_key=config["requires_api_key"],
                    dimension=config["dimension"],
                    description=config.get("description", ""),
                    underlying_model_id=config.get("model_id"),
                ))

            db.commit()
        finally:
            db.close()
    except Exception as exc:
        print(f"[EmbeddingRegistry] Warning: could not persist model '{model_id}' to DB: {exc}")


def load_from_db() -> None:
    """
    Load dynamically registered embedding models from the database
    back into EMBEDDING_MODEL_MAP at startup.

    Built-in models already in EMBEDDING_MODEL_MAP are not overwritten.
    """
    try:
        from database.session import SessionLocal
        from database.models.embedding_config_model import EmbeddingConfigModel

        db = SessionLocal()
        try:
            rows = db.query(EmbeddingConfigModel).all()
            for row in rows:
                if row.model_id not in EMBEDDING_MODEL_MAP:
                    entry: dict = {
                        "name": row.name,
                        "provider": row.provider,
                        "billing": row.billing,
                        "requires_api_key": row.requires_api_key,
                        "dimension": row.dimension,
                        "description": row.description or "",
                    }
                    if row.underlying_model_id:
                        entry["model_id"] = row.underlying_model_id
                    EMBEDDING_MODEL_MAP[row.model_id] = entry
                    print(f"[EmbeddingRegistry] Restored persisted model: {row.model_id}")
        finally:
            db.close()
    except Exception as exc:
        print(f"[EmbeddingRegistry] Warning: could not load models from DB: {exc}")