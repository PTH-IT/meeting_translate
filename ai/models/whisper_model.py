"""Whisper model wrapper."""
import logging
import whisperx
import numpy as np
from typing import List, Dict, Optional
import asyncio
import os


logger = logging.getLogger(__name__)


class WhisperModel:
    """Speech-to-text model wrapper."""
    
    def __init__(self, model_name: str = "large-v3", device: str = "cuda"):
        self.device = "cpu" if not (device == "cuda" and os.environ.get("CUDA_AVAILABLE") == "true") else device
        self.model_name = model_name
        self.model = None
        self.mock_mode = os.environ.get("MOCK_TRANSCRIPTION", "true").lower() == "true"
        logger.info("WhisperModel init: mock_mode=%s model_name=%s device=%s", self.mock_mode, self.model_name, self.device)
        
    async def load_model(self):
        """Load the Whisper model asynchronously."""
        if self.model is None and not self.mock_mode:
            logger.info("WhisperModel loading model: %s on %s", self.model_name, self.device)
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: whisperx.load_model(
                    self.model_name,
                    self.device,
                    compute_type="float16" if self.device == "cuda" else "float32"
                )
            )
            logger.info("WhisperModel load success")
        elif self.model is not None:
            logger.debug("WhisperModel already loaded")
    
    def _mock_transcribe(self, audio: np.ndarray) -> Dict:
        """Mock transcription for testing when models unavailable."""
        max_amp = np.max(np.abs(audio))
        if max_amp < 0.01:
            return {"segments": []}
        return {
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": "hello, this is a test",
                    "words": []
                }
            ]
        }
    
    async def transcribe(
        self, 
        audio: np.ndarray, 
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio to text with timestamps.
        
        Returns segments with word-level timing for speaker diarization alignment.
        """
        if self.mock_mode:
            return self._mock_transcribe(audio)
        
        await self.load_model()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.model.transcribe(
                audio, 
                language=language,
                word_timestamps=True
            )
        )
        
        return result
    
    async def detect_language(self, audio: np.ndarray) -> str:
        """Auto-detect source language from audio."""
        if self.mock_mode:
            return "en"
        await self.load_model()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.model.detect_language(audio)
        )
        return result[0] if result else "en"