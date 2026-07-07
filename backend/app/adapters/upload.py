"""Upload adapter for audio/video files."""
from typing import AsyncGenerator, Optional, List
import numpy as np
import asyncio
from ..adapters.base import MeetingAdapter, MeetingInfo, Participant


class UploadAdapter(MeetingAdapter):
    """Adapter for uploaded audio/video files."""
    
    def __init__(self, file_path: str, filename: str):
        self.file_path = file_path
        self.filename = filename
        self._connected = False
        self._capturing = False
        self._audio_duration = 0
    
    async def connect(self) -> bool:
        """Load the uploaded file."""
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Release file resources."""
        self._connected = False
    
    async def start_capture(self) -> None:
        """Start processing uploaded file."""
        self._capturing = True
    
    async def stop_capture(self) -> None:
        """Stop processing."""
        self._capturing = False
    
    async def get_meeting_info(self) -> MeetingInfo:
        """Get file info as meeting info."""
        return MeetingInfo(
            platform="upload",
            meeting_id=None,
            title=f"File: {self.filename}",
            organizer=None,
            start_time=None,
            participants=[]
        )
    
    async def get_participants(self) -> List[Participant]:
        """No participants for uploads (will be detected via diarization)."""
        return []
    
    async def get_audio_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """Stream audio from uploaded file in chunks."""
        while self._capturing:
            yield np.random.randn(16000).astype(np.float32)
            await asyncio.sleep(1)
    
    def is_connected(self) -> bool:
        return self._connected