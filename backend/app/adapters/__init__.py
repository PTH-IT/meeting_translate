"""Meeting platform adapters."""
from .base import MeetingAdapter, MeetingInfo, Participant
from .zoom import ZoomAdapter
from .teams import TeamsAdapter
from .google_meet import GoogleMeetAdapter
from .discord import DiscordAdapter
from .system_audio import SystemAudioAdapter
from .upload import UploadAdapter

__all__ = [
    "MeetingAdapter",
    "MeetingInfo", 
    "Participant",
    "ZoomAdapter",
    "TeamsAdapter",
    "GoogleMeetAdapter",
    "DiscordAdapter",
    "SystemAudioAdapter",
    "UploadAdapter"
]