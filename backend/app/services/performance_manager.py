"""Performance optimization module for streaming latency."""
import asyncio
import time
from typing import Optional, Callable
from collections import deque


class PerformanceManager:
    """Manage streaming performance and latency targets."""
    
    TARGET_STT_LATENCY = 0.5  # seconds
    TARGET_TRANS_LATENCY = 0.5  # seconds
    TARGET_E2E_LATENCY = 1.0  # seconds
    
    def __init__(self):
        self.metrics = {
            "stt_times": deque(maxlen=100),
            "trans_times": deque(maxlen=100),
            "e2e_times": deque(maxlen=100)
        }
        self.audio_buffer = bytearray()
    
    def track_stt(self, duration: float) -> None:
        """Record STT processing time."""
        self.metrics["stt_times"].append(duration)
    
    def track_translation(self, duration: float) -> None:
        """Record translation processing time."""
        self.metrics["trans_times"].append(duration)
    
    def track_e2e(self, duration: float) -> None:
        """Record end-to-end latency."""
        self.metrics["e2e_times"].append(duration)
    
    def get_average_stt(self) -> float:
        """Get average STT time."""
        times = list(self.metrics["stt_times"])
        return sum(times) / len(times) if times else 0
    
    def get_average_trans(self) -> float:
        """Get average translation time."""
        times = list(self.metrics["trans_times"])
        return sum(times) / len(times) if times else 0
    
    async def process_stream(
        self,
        audio_chunk: bytes,
        stt_callback: Callable,
        trans_callback: Callable
    ):
        """Process audio chunk with latency tracking."""
        start_time = time.time()
        
        # STT
        stt_start = time.time()
        text = await stt_callback(audio_chunk)
        self.track_stt(time.time() - stt_start)
        
        # Translation (parallel for multiple languages)
        trans_start = time.time()
        translations = await asyncio.gather(*[
            trans_callback(text, lang) for lang in ["vi", "en", "ja", "zh"]
        ])
        self.track_translation(time.time() - trans_start)
        
        self.track_e2e(time.time() - start_time)
        
        return text, dict(zip(["vi", "en", "ja", "zh"], translations))