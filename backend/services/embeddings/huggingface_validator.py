from huggingface_hub import HfApi, InferenceClient


def validate_huggingface_embedding(
    model_id: str,
    token: str | None = None,
) -> dict:
    """
    Validate Hugging Face token, model availability,
    embedding inference, and vector dimension.
    """

    model_id = (model_id or "").strip()

    if not model_id:
        return {
            "valid": False,
            "token_valid": False,
            "model_available": False,
            "embedding_supported": False,
            "error": "Hugging Face model ID is required.",
        }

    if not token or not token.strip():
        return {
            "valid": False,
            "token_valid": False,
            "model_available": False,
            "embedding_supported": False,
            "error": "Hugging Face token is required for hosted inference.",
        }

    token = token.strip()
    api = HfApi(token=token)

    # 1. Validate token
    try:
        api.whoami()
        token_valid = True
    except Exception:
        return {
            "valid": False,
            "token_valid": False,
            "model_available": False,
            "embedding_supported": False,
            "error": "Hugging Face token is invalid or unauthorized.",
        }

    # 2. Validate model exists
    try:
        model_info = api.model_info(model_id)
        model_available = True
    except Exception as exc:
        return {
            "valid": False,
            "token_valid": token_valid,
            "model_available": False,
            "embedding_supported": False,
            "error": f"Model '{model_id}' was not found or is inaccessible: {exc}",
        }

    # 3. Validate actual feature extraction
    try:
        client = InferenceClient(
            model=model_id,
            provider="hf-inference",
            token=token,
        )

        result = client.feature_extraction(
            "embedding validation test",
        )

        shape = getattr(result, "shape", None)

        if not shape:
            return {
                "valid": False,
                "token_valid": True,
                "model_available": True,
                "embedding_supported": False,
                "error": "Hugging Face returned no embedding shape.",
            }

        dimension = int(shape[-1])

        return {
            "valid": True,
            "token_valid": True,
            "model_available": model_available,
            "embedding_supported": True,
            "model_id": model_id,
            "pipeline_tag": getattr(model_info, "pipeline_tag", None),
            "dimension": dimension,
        }

    except Exception as exc:
        return {
            "valid": False,
            "token_valid": True,
            "model_available": True,
            "embedding_supported": False,
            "error": f"Embedding inference failed: {exc}",
        }