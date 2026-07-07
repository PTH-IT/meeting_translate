"""Base adapter interface for meeting platforms."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class MeetingInfo:
    """Meeting metadata."""
    platform: str
    meeting_id: Optional[str]
    title: Optional[str]
    organizer: Optional[str]
    start_time: Optional[datetime]
    participants: List[Dict[str, str]]


@dataclass
class Participant:
    """Participant information."""
    id: str
    name: str
    email: Optional[str]
    is_host: bool = False


class MeetingAdapter(ABC):
    """Abstract base class for meeting platform adapters."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to meeting."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from meeting."""
        pass
    
    @abstractmethod
    async def start_capture(self) -> None:
        """Start capturing audio stream."""
        pass
    
    @abstractmethod
    async def stop_capture(self) -> None:
        """Stop capturing audio stream."""
        pass
    
    @abstractmethod
    async def get_meeting_info(self) -> MeetingInfo:
        """Get meeting metadata."""
        pass
    
    @abstractmethod
    async def get_participants(self) -> List[Participant]:
        """Get list of meeting participants."""
        pass
    
    @abstractmethod
    async def get_audio_stream(self) -> AsyncGenerator[np.ndarray, None]:
        """Stream audio chunks."""
        yield np.array([])
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check connection status."""
        pass