"""Backend AI client interface."""
import logging
import os
from typing import Dict, List, Optional

import httpx


logger = logging.getLogger(__name__)


class AIClient:
    """Client for communicating with AI inference service."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("AI_SERVICE_URL", "http://ai:8000")
        self.timeout = httpx.Timeout(30.0)
    
    async def translate(self, text: str, target_lang: str = "vi", source_lang: Optional[str] = None) -> str:
        logger.info("Backend calling AI /translate: text=%r target_lang=%s source_lang=%s", text, target_lang, source_lang or "auto")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {"text": text, "target_lang": target_lang}
            if source_lang:
                payload["source_lang"] = source_lang
            
            resp = await client.post(
                f"{self.base_url}/translate",
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("AI /translate response: %s", data)
            return data.get("translated_text", text)
    
    async def detect_language(self, text: str) -> str:
        logger.info("Backend calling AI /detect-language: text=%r", text)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/detect-language",
                json={"text": text}
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("AI /detect-language response: %s", data)
            return data.get("language", "en")
    
    async def process_audio(self, audio_bytes: bytes, target_langs: List[str] = None, sample_rate: int = 16000, chunk_id: int = None) -> Dict:
        import base64
        if target_langs is None:
            target_langs = ["vi", "en", "ja", "zh"]
        
        logger.info("Backend calling AI /process-audio: bytes=%d target_langs=%s sample_rate=%s chunk_id=%s", len(audio_bytes) if audio_bytes else 0, target_langs, sample_rate, chunk_id)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "audio": base64.b64encode(audio_bytes).decode("utf-8"),
                "target_langs": target_langs,
                "sample_rate": sample_rate
            }
            if chunk_id is not None:
                payload["chunk_id"] = chunk_id
            
            resp = await client.post(
                f"{self.base_url}/process-audio",
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("AI /process-audio response status=%s segments=%d translations_keys=%s", data.get("status"), len(data.get("segments", [])), list(data.get("translations", {}).keys()))
            return data
    
    async def health(self) -> Dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json()

    
    async def health(self) -> Dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json()
