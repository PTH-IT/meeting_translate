"""API routes for meeting translator."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
import base64
import numpy as np
import os

from ..core.ai_client import AIClient

router = APIRouter()
_ai_client = None


def get_ai_client():
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time audio streaming and translation."""
    client = get_ai_client()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            try:
                result = await client.process_audio(
                    data,
                    target_langs=["vi", "en", "ja", "zh"]
                )
                await websocket.send_json(result)
            except Exception:
                await websocket.send_json({"segments": [], "status": "error"})
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close()


@router.websocket("/ws/multi-lang")
async def websocket_multi_lang(websocket: WebSocket):
    """Multi-language translation streaming endpoint."""
    client = get_ai_client()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            import logging
            logger = logging.getLogger(__name__)
            audio_data = data.get("audio", "")
            target_langs = data.get("target_langs", ["vi", "en", "ja", "zh"])
            sample_rate = int(data.get("sample_rate", 16000))
            logger.info("[ws/multi-lang] recv audio_b64_len=%s target_langs=%s sample_rate=%s", len(audio_data) if audio_data else 0, target_langs, sample_rate)
            
            try:
                import base64
                audio_bytes = base64.b64decode(audio_data)
                result = await client.process_audio(
                    audio_bytes,
                    target_langs=target_langs,
                    sample_rate=sample_rate,
                    chunk_id=data.get("chunk_id")
                )
                # Debug: see if STT produced any segments
                segments = (result.get("segments") or []) if isinstance(result, dict) else []
                first_text = None
                if segments and isinstance(segments, list):
                    # meeting_pipeline returns segments like {speaker,text,translation,...}
                    first_text = segments[0].get("text") if isinstance(segments[0], dict) else None
                import logging
                logger = logging.getLogger(__name__)
                logger.info("[ws/multi-lang] segments_len=%s first_text=%r", len(segments), first_text)
                await websocket.send_json(result)
            except Exception as e:
                await websocket.send_json({
                    "error": str(e),
                    "status": "error"
                })
    except WebSocketDisconnect:
        pass


@router.post("/translate")
async def translate_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_languages: str = Form("vi")
):
    """Upload audio/video file for offline translation."""
    content = await file.read()
    target_lang_list = target_languages.split(",")
    
    background_tasks.add_task(
        process_uploaded_file,
        content,
        file.filename,
        target_lang_list
    )
    
    return {"status": "processing", "filename": file.filename, "target_languages": target_lang_list}


async def process_uploaded_file(content: bytes, filename: str, target_languages: list):
    """Process uploaded file in background."""
    client = get_ai_client()
    try:
        result = await client.process_audio(content, target_langs=target_languages)
    except Exception:
        result = {"status": "error", "segments": []}


async def process_audio_chunk(
    audio: np.ndarray,
    target_langs: list = None,
    sample_rate: int = 16000
) -> dict:
    """Process a single audio chunk and return translation."""
    client = get_ai_client()
    if target_langs is None:
        target_langs = ["vi", "en", "ja", "zh"]
    
    audio_bytes = audio.tobytes()
    return await client.process_audio(audio_bytes, target_langs=target_langs, sample_rate=sample_rate)
