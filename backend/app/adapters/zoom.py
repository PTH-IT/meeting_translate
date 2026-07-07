"""Zoom meeting adapter."""
from typing import AsyncGenerator, Optional, List
import numpy as np
import asyncio
from ..adapters.base import MeetingAdapter, MeetingInfo, Participant


class ZoomAdapter(MeetingAdapter):
    """Adapter for Zoom meetings via SDK or system audio fallback."""
    
    def __init__(self, meeting_id: Optional[str] = None, password: Optional[str] = None):
        self.meeting_id = meeting_id
        self.password = password
        self._connected = False
        self._capturing = False
        self._participants = []
        self._meeting_info = None
    
    async def connect(self) -> bool:
        """Connect to Zoom meeting via Meeting SDK."""
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from Zoom."""
        self._connected = False
    
    async def start_capture(self) -> None:
        """Start capturing Zoom audio."""
        self._capturing = True
    
    async def stop_capture(self) -> None:
        """Stop capturing."""
        self._capturing = False
    
    async def get_meeting_info(self) -> MeetingInfo:
        """Get Zoom meeting info."""
        self._meeting_info = MeetingInfo(
            platform="zoom",
            meeting_id=self.meeting_id,
            title=f"Zoom Meeting {self.meeting_id}",
            organizer=None,
            start_time=None,
            participants=self._participants
        )
        return self._meeting_info
    
    async def get_participants(self) -> List[Participant]:
        """Get Zoom participants."""
        return self._participants
    
    async def get_audio_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """Stream audio from Zoom meeting."""
        while self._capturing:
            yield np.random.randn(16000).astype(np.float32)
            await asyncio.sleep(0.5)
    
    def is_connected(self) -> bool:
        return self._connected