"""FFmpeg audio processing service."""
import ffmpeg
import numpy as np
from typing import Tuple
import tempfile
import os


class FFmpegService:
    """Audio preprocessing and format conversion using FFmpeg."""
    
    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and convert to mono 16kHz numpy array.
        
        Returns: (audio_array, sample_rate)
        """
        out, _ = (
            ffmpeg
            .input(file_path)
            .output('pipe:', format='f32le', acodec='pcm_float', ac=1, ar='16000')
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        audio = np.frombuffer(out, dtype=np.float32)
        return audio, 16000
    
    @staticmethod
    def resample(audio: np.ndarray, sample_rate: int, target_rate: int = 16000) -> np.ndarray:
        """Resample audio to target sample rate."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Write input audio
        ffmpeg.input('pipe:', format='f32le', ac='1', ar=str(sample_rate)).output(tmp_path).run(
            input=audio.tobytes(),
            capture_stdout=True,
            capture_stderr=True
        )
        
        # Read resampled audio
        out, _ = (
            ffmpeg
            .input(tmp_path)
            .output('pipe:', format='f32le', acodec='pcm_float', ac=1, ar=str(target_rate))
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        os.unlink(tmp_path)
        return np.frombuffer(out, dtype=np.float32)
    
    @staticmethod
    def extract_audio_from_video(video_path: str) -> str:
        """Extract audio track from video file, return temp audio path."""
        audio_path = tempfile.mktemp(suffix='.wav')
        
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .run(overwrite_output=True)
        )
        
        return audio_path
    
    @staticmethod
    def create_chunks(audio: np.ndarray, chunk_duration: float = 5.0, sample_rate: int = 16000) -> list:
        """Split audio into chunks for streaming processing."""
        chunk_samples = int(chunk_duration * sample_rate)
        chunks = []
        
        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) > 0:
                chunks.append((chunk, i / sample_rate))
        
        return chunks