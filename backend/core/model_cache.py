import gc

class ModelCache:
    """
    Singleton cache for heavy local models like SentenceTransformers and CrossEncoders.
    Prevents loading the same model multiple times into memory.
    """
    _models = {}

    @classmethod
    def get_sentence_transformer(cls, model_name: str):
        if model_name not in cls._models:
            print(f"[ModelCache] Loading SentenceTransformer: {model_name}")
            from sentence_transformers import SentenceTransformer
            cls._models[model_name] = SentenceTransformer(model_name, device="cpu")
        return cls._models[model_name]

    @classmethod
    def get_cross_encoder(cls, model_name: str):
        if model_name not in cls._models:
            print(f"[ModelCache] Loading CrossEncoder: {model_name}")
            from sentence_transformers import CrossEncoder
            cls._models[model_name] = CrossEncoder(model_name, device="cpu")
        return cls._models[model_name]
    
    @classmethod
    def clear(cls):
        cls._models.clear()
        gc.collect()
