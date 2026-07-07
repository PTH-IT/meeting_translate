"""Realtime inference orchestration."""
import asyncio
from typing import Dict, List, Optional, Callable

from ai.pipelines.transcription_pipeline import TranscriptionPipeline
from ai.pipelines.diarization_pipeline import DiarizationPipeline
from ai.pipelines.translation_pipeline import TranslationPipeline
from ai.pipelines.meeting_pipeline import MeetingPipeline


class InferenceOrchestrator:
    """Orchestrate realtime AI inference."""
    
    def __init__(self):
        self.transcription = TranscriptionPipeline()
        self.diarization = DiarizationPipeline()
        self.translation = TranslationPipeline()
        self.meeting = MeetingPipeline()
    
    async def process_audio_chunk(self, audio, whisper=None, diarization=None, sample_rate: int = 16000) -> Dict:
        if whisper is None:
            whisper = self.transcription
        if diarization is None:
            diarization = self.diarization
        
        transcript = await whisper.process(audio, sample_rate)
        segments = transcript.get("segments", [])
        
        if not segments:
            return {"segments": []}
        
        segments = await diarization.process(audio, segments, sample_rate)
        
        result_segments = []
        for seg in segments:
            if seg.get("text"):
                trans = await self.translation.translate(seg["text"])
                result_segments.append({
                    "speaker": seg.get("speaker", "Unknown"),
                    "text": seg["text"],
                    "translation": trans,
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0)
                })
        
        return {"segments": result_segments}
