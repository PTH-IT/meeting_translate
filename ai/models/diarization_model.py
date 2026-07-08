"""Diarization model wrapper using pyannote.audio."""
import logging
from typing import List, Dict
import asyncio
import numpy as np
import os


logger = logging.getLogger(__name__)


class DiarizationModel:
    """Speaker diarization model wrapper."""
    
    def __init__(self, model_name: str = "pyannote/speaker-diarization-3.1"):
        self.model_name = model_name
        self.pipeline = None
        self.mock_mode = os.environ.get("MOCK_DIARIZATION", "true").lower() == "true"
        logger.info("DiarizationModel init: mock_mode=%s model_name=%s", self.mock_mode, self.model_name)
        
    async def load_model(self):
        if self.pipeline is None and not self.mock_mode:
            try:
                logger.info("DiarizationModel loading pipeline: %s", self.model_name)
                import torch
                from pyannote.audio import Pipeline
                loop = asyncio.get_event_loop()
                self.pipeline = await loop.run_in_executor(
                    None,
                    lambda: Pipeline.from_pretrained(
                        self.model_name,
                        use_auth_token=None
                    )
                )
                logger.info("DiarizationModel load success")
            except ImportError:
                logger.exception("DiarizationModel load failed, fallback to mock mode")
                self.mock_mode = True
        elif self.pipeline is not None:
            logger.debug("DiarizationModel already loaded")
    
    def _mock_diarize(self, audio: np.ndarray) -> List[Dict]:
        return [
            {"start": 0.0, "end": len(audio) / 16000, "speaker": "Speaker_1"}
        ]
    
    async def diarize(
        self, 
        audio: np.ndarray, 
        sample_rate: int = 16000,
        num_speakers: int = None
    ) -> List[Dict]:
        if self.mock_mode:
            return self._mock_diarize(audio)
        
        await self.load_model()
        
        import torch
        loop = asyncio.get_event_loop()
        diarization = await loop.run_in_executor(
            None,
            lambda: self.pipeline({"waveform": torch.from_numpy(audio), "sample_rate": sample_rate})
        )
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": f"Speaker_{speaker}"
            })
        
        return segments
    
    def assign_speakers_to_transcript(
        self, 
        transcript_segments: List[Dict],
        diarization_segments: List[Dict]
    ) -> List[Dict]:
        """
        Assign speaker labels to transcript segments based on timing overlap.
        
        Each transcript segment gets the speaker label of the diarization segment
        with maximum overlap in time.
        """
        for seg in transcript_segments:
            seg_start = seg.get("start", 0)
            seg_end = seg.get("end", 0)
            
            best_speaker = "Unknown"
            best_overlap = 0
            
            for dia_seg in diarization_segments:
                overlap_start = max(seg_start, dia_seg["start"])
                overlap_end = min(seg_end, dia_seg["end"])
                overlap = max(0, overlap_end - overlap_start)
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_speaker = dia_seg["speaker"]
            
            seg["speaker"] = best_speaker
        
        return transcript_segments