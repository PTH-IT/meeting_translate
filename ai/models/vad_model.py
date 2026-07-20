"""Voice Activity Detection model wrapper."""
import logging
import os
from typing import Tuple

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    np = None

try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - exercised in lightweight environments
    torch = None


logger = logging.getLogger(__name__)


class VADModel:
    """Detect speech segments in audio for optimal chunking."""
    
    def __init__(self, threshold: float = 0.5, min_speech_ms: int = 250):
        self.threshold = threshold
        self.min_speech_ms = min_speech_ms
        self.model = None
        self.vad_utils = None
        self.mock_mode = os.environ.get("MOCK_VAD", "true").lower() == "true"
        logger.info("VADModel init: mock_mode=%s threshold=%s min_speech_ms=%s", self.mock_mode, self.threshold, self.min_speech_ms)
        
    def load_model(self):
        if self.model is None and not self.mock_mode:
            if torch is None:
                logger.warning("Torch is unavailable; falling back to mock VAD")
                self.mock_mode = True
                return
            try:
                logger.info("VADModel loading silero-vad from torch hub")
                loaded = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad'
                )
                if isinstance(loaded, tuple):
                    self.model = loaded[0]
                    self.vad_utils = loaded[1]
                else:
                    self.model = loaded
                logger.info("VADModel load success")
            except ImportError:
                logger.exception("VADModel load failed, fallback to mock mode")
                self.mock_mode = True
        elif self.model is not None:
            logger.debug("VADModel already loaded")
    
    
    def _mock_speech_check(self, audio) -> list:
        if np is not None:
            max_amp = np.max(np.abs(audio))
            if max_amp > 0.01 and len(audio) > 1000:
                return [{"start": 0, "end": len(audio) / 16000}]
            return []

        if hasattr(audio, "__len__") and len(audio) > 1000:
            return [{"start": 0, "end": len(audio) / 16000}]
        return []
    
    def get_speech_timestamps(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000
    ) -> list:
        if self.mock_mode:
            return self._mock_speech_check(audio)
        
        self.load_model()
        
        if torch is not None and np is not None and isinstance(audio, np.ndarray):
            audio_tensor = torch.from_numpy(audio).float()
        else:
            audio_tensor = audio
            
        if self.vad_utils is not None and callable(self.vad_utils[0]):
            speech_ts = self.vad_utils[0](
                audio_tensor,
                self.model,
                threshold=self.threshold,
                min_speech_duration_ms=self.min_speech_ms,
                sampling_rate=sample_rate
            )
        else:
            speech_ts = self.model(
                audio_tensor,
                sample_rate,
                threshold=self.threshold,
                min_speech_duration_ms=self.min_speech_ms
            )
        
        return [
            {
                "start": ts['start'] / sample_rate,
                "end": ts['end'] / sample_rate
            }
            for ts in speech_ts
        ]
    
    def merge_timestamps(self, segments: list) -> list:
        """Merge overlapping/adjacent speech segments."""
        if not segments:
            return []
        
        merged = []
        for seg in sorted(segments, key=lambda x: x['start']):
            if merged and seg['start'] <= merged[-1]['end']:
                merged[-1]['end'] = max(merged[-1]['end'], seg['end'])
            else:
                merged.append(seg)
        
        return merged
    
    def get_vad_chunks(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000
    ) -> Tuple[list, list]:
        """
        Split audio into speech/non-speech chunks.
        
        Returns: (speech_chunks, timestamps)
        """
        speech_ts = self.get_speech_timestamps(audio, sample_rate)
        speech_ts = self.merge_timestamps(speech_ts)
        
        chunks = []
        timestamps = []
        
        for ts in speech_ts:
            start_sample = int(ts['start'] * sample_rate)
            end_sample = int(ts['end'] * sample_rate)
            chunk = audio[start_sample:end_sample]
            if len(chunk) > 0:
                chunks.append(chunk)
                timestamps.append(ts)
        
        return chunks, timestamps