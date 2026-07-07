"""Diarization pipeline: speaker identification + assignment."""
import os
from typing import Dict, List, Optional

from ai.models.diarization_model import DiarizationModel
from ai.postprocess.output_formatter import OutputFormatter


class DiarizationPipeline:
    """Speaker diarization pipeline."""
    
    def __init__(self):
        self.model = DiarizationModel()
        self.formatter = OutputFormatter()
        self.mock_mode = os.environ.get("MOCK_DIARIZATION", "true").lower() == "true"
    
    async def process(self, audio, transcript_segments: List[Dict], sample_rate: int = 16000) -> List[Dict]:
        if self.mock_mode:
            speakers = [{"start": 0.0, "end": len(audio) / 16000, "speaker": "Speaker_1"}]
        else:
            speakers = await self.model.diarize(audio, sample_rate)
        
        return self.model.assign_speakers_to_transcript(transcript_segments, speakers)
