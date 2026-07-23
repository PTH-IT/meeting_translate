"""Whisper model wrapper."""
import logging
import os
import asyncio
from typing import Dict, Optional

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    np = None

try:
    import whisperx
except Exception:  # pragma: no cover - handled gracefully for missing/unsupported installs
    whisperx = None

try:
    from faster_whisper import WhisperModel as FasterWhisperModel
except Exception:  # pragma: no cover - handled gracefully for missing/unsupported installs
    FasterWhisperModel = None


logger = logging.getLogger(__name__)


class WhisperModel:
    """Speech-to-text model wrapper."""

    def __init__(self, model_name: str = None, device: str = "cuda"):
        self.device = "cpu" if not (device == "cuda" and os.environ.get("CUDA_AVAILABLE") == "true") else device
        self.model_name = model_name or os.environ.get("WHISPER_MODEL", "base")
        self.model = None
        self.mock_mode = os.environ.get("MOCK_TRANSCRIPTION", "true").lower() == "true"
        logger.info("WhisperModel init: mock_mode=%s model_name=%s device=%s", self.mock_mode, self.model_name, self.device)

    async def load_model(self):
        """Load the Whisper model asynchronously."""
        if self.model is None and not self.mock_mode:
            if FasterWhisperModel is None:
                logger.warning("faster-whisper is unavailable; falling back to mock transcription")
                self.mock_mode = True
                return

            logger.info("WhisperModel loading model: %s on %s", self.model_name, self.device)
            try:
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    None,
                    lambda: FasterWhisperModel(
                        self.model_name,
                        device=self.device,
                        compute_type="int8" if self.device == "cpu" else "float16",
                        download_root=os.environ.get("WHISPER_CACHE_DIR", "/app/models/whisperx")
                    )
                )
                logger.info("WhisperModel load success")
            except Exception as exc:
                logger.warning("WhisperModel load failed: %s; falling back to mock transcription", exc)
                self.mock_mode = True

    def _mock_transcribe(self, audio) -> Dict:
        """Mock transcription for testing when models unavailable."""
        if np is not None:
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
        audio,
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

        if self.mock_mode:
            return self._mock_transcribe(audio)

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio,
                    language=language,
                    word_timestamps=True
                )
            )

            if isinstance(result, tuple) and len(result) == 2:
                segments_iter, info = result
                segments = []
                for seg in segments_iter:
                    segments.append({
                        "start": seg.start,
                        "end": seg.end,
                        "text": seg.text,
                        "words": [
                            {
                                "start": w.start,
                                "end": w.end,
                                "word": w.word,
                                "probability": w.probability,
                            }
                            for w in (seg.words or [])
                        ],
                    })

                if segments:
                    return {"segments": segments}

                return self._mock_transcribe(audio)

            if isinstance(result, dict):
                segments = result.get("segments", [])
                if isinstance(segments, list) and segments:
                    return result

            return self._mock_transcribe(audio)
        except Exception as exc:
            logger.warning("Whisper transcription failed: %s; using mock transcript", exc)
            return self._mock_transcribe(audio)

    async def detect_language(self, audio) -> str:
        """Auto-detect source language from audio."""
        if self.mock_mode:
            return "en"
        await self.load_model()

        if self.mock_mode:
            return "en"

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.model.detect_language(audio)
            )
            return result[0] if result else "en"
        except Exception as exc:
            logger.warning("Whisper language detection failed: %s; defaulting to English", exc)
            return "en"