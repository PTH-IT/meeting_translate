"""System audio adapter for capturing local audio."""
from typing import AsyncGenerator, Optional
import numpy as np
import asyncio
from ..adapters.base import MeetingAdapter, MeetingInfo, Participant


class SystemAudioAdapter(MeetingAdapter):
    """Adapter for system audio capture (microphone/system audio)."""
    
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self._connected = False
        self._capturing = False
        self._participants = [{
            "id": "local",
            "name": "Local Microphone",
            "email": None
        }]
    
    async def connect(self) -> bool:
        """Connect to system audio device."""
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from audio device."""
        self._connected = False
    
    async def start_capture(self) -> None:
        """Start capturing from system audio."""
        self._capturing = True
    
    async def stop_capture(self) -> None:
        """Stop capturing."""
        self._capturing = False
    
    async def get_meeting_info(self) -> MeetingInfo:
        """Get system audio info."""
        return MeetingInfo(
            platform="system_audio",
            meeting_id=None,
            title="Local Audio Input",
            organizer=None,
            start_time=None,
            participants=self._participants
        )
    
    async def get_participants(self) -> list:
        """Get local participants."""
        return self._participants
    
    async def get_audio_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """Stream audio from system (simulation mode)."""
        while self._capturing:
            yield np.random.randn(16000).astype(np.float32)
            await asyncio.sleep(1)
    
    def is_connected(self) -> bool:
        return self._connected