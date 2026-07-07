"""Transcription pipeline: VAD + Whisper."""
import os
from typing import Dict, List, Optional

from ai.models.vad_model import VADModel
from ai.models.whisper_model import WhisperModel
from ai.preprocess.audio_preprocessor import AudioPreprocessor
from ai.postprocess.output_formatter import OutputFormatter


class TranscriptionPipeline:
    """End-to-end speech-to-text pipeline."""
    
    def __init__(self):
        self.vad = VADModel()
        self.whisper = WhisperModel()
        self.preprocessor = AudioPreprocessor()
        self.formatter = OutputFormatter()
        self.mock_vad = os.environ.get("MOCK_VAD", "true").lower() == "true"
        self.mock_stt = os.environ.get("MOCK_TRANSCRIPTION", "true").lower() == "true"
    
    async def process(self, audio: bytes, sample_rate: int = 16000) -> Dict:
        import numpy as np
        audio_np = np.frombuffer(audio, dtype=np.float32)
        audio_np = self.preprocessor.normalize(audio_np)
        
        if self.mock_vad or len(audio_np) == 0:
            segments = [{"start": 0, "end": len(audio_np) / 16000, "text": "hello test", "speaker": "Speaker_1"}]
        else:
            speech_timestamps = self.vad.get_speech_timestamps(audio_np, sample_rate)
            if not speech_timestamps:
                return {"segments": []}
            
            transcript = await self.whisper.transcribe(audio_np, sample_rate)
            segments = transcript.get("segments", [])
        
        return {"segments": segments}
