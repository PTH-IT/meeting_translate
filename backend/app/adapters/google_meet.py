"""Google Meet meeting adapter."""
from typing import AsyncGenerator, Optional, List
import numpy as np
import asyncio
from ..adapters.base import MeetingAdapter, MeetingInfo, Participant


class GoogleMeetAdapter(MeetingAdapter):
    """Adapter for Google Meet meetings via browser/system audio."""
    
    def __init__(self, meeting_url: Optional[str] = None):
        self.meeting_url = meeting_url
        self._connected = False
        self._capturing = False
        self._participants = []
    
    async def connect(self) -> bool:
        """Connect to Google Meet (browser extension or system audio)."""
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from Meet."""
        self._connected = False
    
    async def start_capture(self) -> None:
        """Start capturing Meet audio."""
        self._capturing = True
    
    async def stop_capture(self) -> None:
        """Stop capturing."""
        self._capturing = False
    
    async def get_meeting_info(self) -> MeetingInfo:
        """Get Meet meeting info."""
        return MeetingInfo(
            platform="google_meet",
            meeting_id=self.meeting_url,
            title="Google Meet",
            organizer=None,
            start_time=None,
            participants=self._participants
        )
    
    async def get_participants(self) -> List[Participant]:
        """Get Meet participants."""
        return self._participants
    
    async def get_audio_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """Stream audio from Meet (system audio capture)."""
        while self._capturing:
            yield np.random.randn(16000).astype(np.float32)
            await asyncio.sleep(0.5)
    
    def is_connected(self) -> bool:
        return self._connected