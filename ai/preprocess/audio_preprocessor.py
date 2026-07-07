"""Audio preprocessing and feature extraction."""
import numpy as np


class AudioPreprocessor:
    """Preprocess audio for AI models."""
    
    @staticmethod
    def normalize(audio: np.ndarray) -> np.ndarray:
        audio = audio - np.mean(audio)
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        return audio
    
    @staticmethod
    def to_mono(audio: np.ndarray) -> np.ndarray:
        if audio.ndim > 1:
            return np.mean(audio, axis=1)
        return audio
