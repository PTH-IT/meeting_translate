"""Speaker management service - resolves speaker names from SDKs."""
from typing import Dict, Optional
from ..adapters.base import Participant


class SpeakerManager:
    """Manages speaker identity across platforms."""
    
    def __init__(self):
        self.speaker_map: Dict[str, str] = {}  # speaker_id -> display_name
        self.participants: Dict[str, Participant] = {}
    
    def register_speaker(self, participant: Participant) -> None:
        """Register a participant with their speaker label."""
        self.participants[participant.id] = participant
        if participant.name:
            self.speaker_map[participant.id] = participant.name
    
    def resolve_speaker_name(self, speaker_label: str, participants: list) -> str:
        """Replace generic speaker label with actual name if available."""
        # speaker_label format: Speaker_0, Speaker_1, etc.
        speaker_num = speaker_label.replace("Speaker_", "")
        
        for participant in participants:
            if str(participant.get("id", "")) == speaker_num:
                return participant.get("name", speaker_label)
            if participant.get("name") and participant.get("name") in speaker_label:
                return participant["name"]
        
        return speaker_label
    
    def update_speakers(self, new_speakers: Dict[str, str]) -> None:
        """Update speaker mappings from external API."""
        self.speaker_map.update(new_speakers)
    
    def get_speaker_name(self, speaker_id: str, fallback: str) -> str:
        """Get speaker display name or return fallback."""
        return self.speaker_map.get(speaker_id, fallback)