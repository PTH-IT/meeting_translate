"""Discord meeting adapter."""
from typing import AsyncGenerator, Optional, List
import numpy as np
import asyncio
from ..adapters.base import MeetingAdapter, MeetingInfo, Participant


class DiscordAdapter(MeetingAdapter):
    """Adapter for Discord voice channels."""
    
    def __init__(self, channel_id: Optional[str] = None):
        self.channel_id = channel_id
        self._connected = False
        self._capturing = False
        self._participants = []
    
    async def connect(self) -> bool:
        """Connect to Discord voice channel."""
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Disconnect from Discord."""
        self._connected = False
    
    async def start_capture(self) -> None:
        """Start capturing Discord audio."""
        self._capturing = True
    
    async def stop_capture(self) -> None:
        """Stop capturing."""
        self._capturing = False
    
    async def get_meeting_info(self) -> MeetingInfo:
        """Get Discord channel info."""
        return MeetingInfo(
            platform="discord",
            meeting_id=self.channel_id,
            title=f"Discord Channel {self.channel_id}",
            organizer=None,
            start_time=None,
            participants=self._participants
        )
    
    async def get_participants(self) -> List[Participant]:
        """Get Discord participants."""
        return self._participants
    
    async def get_audio_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """Stream audio from Discord."""
        while self._capturing:
            yield np.random.randn(16000).astype(np.float32)
            await asyncio.sleep(0.5)
    
    def is_connected(self) -> bool:
        return self._connected