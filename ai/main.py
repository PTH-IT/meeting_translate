"""FastAPI main application for AI translation service."""
import base64
import io
import struct
from typing import List, Dict, Optional

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    np = None

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ai.pipelines.translation_pipeline import TranslationPipeline
from ai.pipelines.meeting_pipeline import MeetingPipeline
from ai.inference.orchestrator import InferenceOrchestrator
from ai.preprocess.audio_preprocessor import AudioPreprocessor

app = FastAPI(
    title="AI Inference Service",
    description="Multilingual meeting translation microservice",
    version="1.0.0"
)

translation_pipeline = TranslationPipeline()
meeting_pipeline = MeetingPipeline()
orchestrator = InferenceOrchestrator()


class TranslateRequest(BaseModel):
    text: str
    source_lang: str | None = None
    target_lang: str = "vi"


class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str


class LanguageDetectRequest(BaseModel):
    text: str


class LanguageDetectResponse(BaseModel):
    language: str


class ProcessAudioRequest(BaseModel):
    audio: str
    target_langs: List[str] = ["vi", "en", "ja", "zh"]
    sample_rate: int = 16000
    chunk_id: Optional[int] = None
    audio_format: str = "auto"  # "auto", "float32", "int16", "wav"


def decode_audio(audio_data: bytes, audio_format: str, sample_rate: int):
    """Decode raw/encoded audio bytes into a float32 mono array in [-1, 1].

    The client transports audio as base64. It may be:
      * a WAV/RIFF container
      * raw int16 PCM (common from recorders / MediaRecorder)
      * raw float32 PCM (the project's internal numpy format)
    Blindly interpreting int16 bytes as float32 makes every sample ~0, so VAD
    reports silence and the transcription returns empty segments.
    """
    audio_format = (audio_format or "auto").lower()

    if audio_format in ("auto", "wav") and audio_data[:4] == b"RIFF":
        try:
            import soundfile as sf
            data, sr = sf.read(io.BytesIO(audio_data), dtype="float32", always_2d=False)
            if np is not None:
                data = np.asarray(data, dtype=np.float32)
            if data.ndim > 1:
                data = np.mean(data, axis=1) if np is not None else [sum(channel) / len(channel) for channel in data]
            if sr != sample_rate:
                data = AudioPreprocessor.resample(data, sr, sample_rate)
            return data
        except Exception:
            pass

    fmt = audio_format
    if fmt == "auto":
        if len(audio_data) % 4 != 0 and len(audio_data) % 2 == 0:
            fmt = "int16"
        else:
            try:
                if np is None:
                    raise ImportError("numpy not available")
                as_i16 = np.frombuffer(audio_data, dtype=np.int16)
                as_f32 = np.frombuffer(audio_data, dtype=np.float32)
                i16_amp = float(np.max(np.abs(as_i16))) if as_i16.size else 0.0
                # int16 audio reinterpreted as float32 yields huge values
                # (~1e38) for ~half the samples and NaNs for the rest,
                # whereas genuine float32 audio stays within [-1.2, 1.2].
                f32_finite = as_f32[np.isfinite(as_f32)]
                outlier_frac = float(np.mean(np.abs(f32_finite) > 1.0)) if f32_finite.size else 0.0
                if i16_amp > 1.0 and outlier_frac > 0.01:
                    fmt = "int16"
                else:
                    fmt = "float32"
            except Exception:
                fmt = "float32"

    if fmt in ("int16", "pcm16"):
        if np is None:
            arr = [float(int.from_bytes(audio_data[i:i+2], byteorder="little", signed=True)) / 32768.0 for i in range(0, len(audio_data), 2)]
        else:
            arr = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    else:
        if np is None:
            arr = [struct.unpack("<f", audio_data[i:i+4])[0] for i in range(0, len(audio_data), 4)]
        else:
            arr = np.frombuffer(audio_data, dtype=np.float32)

    if np is not None and hasattr(arr, "ndim") and arr.ndim > 1:
        arr = np.mean(arr, axis=1)
    return arr




class ProcessAudioResponse(BaseModel):
    segments: List[Dict]
    translations: Dict
    target_langs: List[str]
    status: str
    chunk_id: int | None = None
    error: str | None = None


@app.post("/process-audio", response_model=ProcessAudioResponse)
async def process_audio(request: ProcessAudioRequest):
    import logging
    logger = logging.getLogger(__name__)
    try:
        audio_data = base64.b64decode(request.audio)
        audio_np = decode_audio(audio_data, request.audio_format, request.sample_rate)
        logger.info("[process-audio] audio_bytes=%d samples=%d sample_rate=%s format=%s amp=%s", len(audio_data), len(audio_np), request.sample_rate, request.audio_format, float(np.max(np.abs(audio_np))) if audio_np.size else 0.0)
        result = await meeting_pipeline.process(audio_np, sample_rate=request.sample_rate, target_langs=request.target_langs)
        if request.chunk_id is not None:
            result["chunk_id"] = request.chunk_id
        result.setdefault("status", "success")
        return ProcessAudioResponse(**result)
    except Exception as e:
        logger.exception("[process-audio] failed: %s", e)
        return ProcessAudioResponse(
            segments=[],
            translations={},
            target_langs=request.target_langs,
            status="error",
            error=str(e)
        )
