"""FastAPI main application for AI translation service."""
from typing import List, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ai.pipelines.translation_pipeline import TranslationPipeline
from ai.pipelines.meeting_pipeline import MeetingPipeline
from ai.inference.orchestrator import InferenceOrchestrator

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
    chunk_id: int | None = None


class ProcessAudioResponse(BaseModel):
    segments: List[Dict]
    translations: Dict
    target_langs: List[str]
    status: str
    chunk_id: int | None = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    translated = await translation_pipeline.translate(
        request.text,
        target_lang=request.target_lang
    )
    return TranslateResponse(
        translated_text=translated,
        source_lang=request.source_lang or "en",
        target_lang=request.target_lang
    )


@app.post("/detect-language", response_model=LanguageDetectResponse)
async def detect_language(request: LanguageDetectRequest):
    lang = await translation_pipeline.detect_language(request.text)

    return LanguageDetectResponse(language=lang)


@app.post("/process-audio", response_model=ProcessAudioResponse)
async def process_audio(request: ProcessAudioRequest):
    import base64
    import numpy as np
    audio_data = base64.b64decode(request.audio)
    audio_np = np.frombuffer(audio_data, dtype=np.float32)
    result = await meeting_pipeline.process(audio_np, sample_rate=request.sample_rate, target_langs=request.target_langs)
    if request.chunk_id is not None:
        result["chunk_id"] = request.chunk_id
    return ProcessAudioResponse(**result)
