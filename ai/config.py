"""Configuration for the real-time meeting translator."""
import os
from pathlib import Path

# Model paths
MODEL_CACHE_DIR = Path(os.getenv("MODEL_CACHE_DIR", Path.home() / ".cache" / "models"))
WHISPER_MODEL = "large-v3"
DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
TRANSLATION_MODEL = "google/gemma-2b"

# Supported languages
SUPPORTED_LANGUAGES = ["vi", "en", "ja", "zh"]
LANGUAGE_NAMES = {"vi": "Vietnamese", "en": "English", "ja": "Japanese", "zh": "Chinese"}

# WebSocket settings
CHUNK_DURATION = 5  # seconds
SAMPLE_RATE = 16000
CHANNELS = 1