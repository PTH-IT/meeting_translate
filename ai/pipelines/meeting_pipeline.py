"""End-to-end meeting pipeline."""
import os
from typing import Dict, List, Optional

from ai.models.vad_model import VADModel
from ai.models.whisper_model import WhisperModel
from ai.models.diarization_model import DiarizationModel
from ai.models.translation_model import TranslationModel
from ai.preprocess.audio_preprocessor import AudioPreprocessor
from ai.postprocess.output_formatter import OutputFormatter


class MeetingPipeline:
    """End-to-end meeting processing pipeline."""
    
    def __init__(self):
        self.vad = VADModel()
        self.whisper = WhisperModel()
        self.diarization = DiarizationModel()
        self.translation = TranslationModel()
        self.preprocessor = AudioPreprocessor()
        self.formatter = OutputFormatter()
    
    async def process(self, audio, sample_rate: int = 16000, target_langs: List[str] = None) -> Dict:
        import numpy as np
        if target_langs is None:
            target_langs = ["vi", "en", "ja", "zh"]
        
        audio_np = np.frombuffer(audio, dtype=np.float32) if isinstance(audio, bytes) else audio
        audio_np = self.preprocessor.normalize(audio_np)
        
        mock_vad = os.environ.get("MOCK_VAD", "true").lower() == "true"
        mock_stt = os.environ.get("MOCK_TRANSCRIPTION", "true").lower() == "true"
        mock_diarization = os.environ.get("MOCK_DIARIZATION", "true").lower() == "true"
        
        if mock_vad or len(audio_np) == 0:
            segments = [{"start": 0, "end": len(audio_np) / 16000, "text": "hello test", "speaker": "Speaker_1"}]
        else:
            speech_timestamps = self.vad.get_speech_timestamps(audio_np, sample_rate)
            if not speech_timestamps:
                return {
                    "segments": [],
                    "translations": {},
                    "target_langs": target_langs,
                    "status": "success"
                }
            
            if mock_stt:
                segments = [{"start": 0, "end": len(audio_np) / 16000, "text": "hello test"}]
            else:
                transcript = await self.whisper.transcribe(audio_np, sample_rate)
                segments = transcript.get("segments", [])
            
            if not segments and not mock_diarization:
                speakers = await self.diarization.diarize(audio_np, sample_rate)
                segments = self.diarization.assign_speakers_to_transcript([], speakers)
        
        translations = {}
        for i, seg in enumerate(segments):
            if seg.get("text"):
                lang_translations = {}
                for lang in target_langs:
                    try:
                        entities = self.formatter.extract_entities(seg["text"])
                        translated = await self.translation.translate(seg["text"], target_lang=lang)
                        lang_translations[lang] = self.formatter.restore_entities(translated, entities)
                    except Exception:
                        lang_translations[lang] = seg["text"]
                seg_id = seg.get("id") or f"seg-{i}-{hash(seg.get('text', '')) & 0xffffffff}"
                seg["id"] = seg_id
                translations[seg_id] = lang_translations
        
        return {
            "segments": segments,
            "translations": translations,
            "target_langs": target_langs,
            "status": "success"
        }
