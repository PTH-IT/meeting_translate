"""Model loading, downloading, caching, and initialization."""
import os
from typing import Any, Dict, Optional


class ModelLoader:
    """Load and cache AI models."""
    
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def get_model(cls, key: str, loader: callable, *args, **kwargs) -> Any:
        if key not in cls._cache:
            cls._cache[key] = loader(*args, **kwargs)
        return cls._cache[key]
    
    @classmethod
    def clear_cache(cls):
        cls._cache.clear()
