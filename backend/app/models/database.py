"""Database models for meeting translator."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TranslationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Speaker(BaseModel):
    """Speaker entity."""
    id: Optional[str] = None
    name: str
    avatar: Optional[str] = None


class TranscriptSegment(BaseModel):
    """Single transcript segment with speaker and translation."""
    id: Optional[str] = None
    speaker_id: Optional[str] = None
    speaker_name: str = "Unknown"
    start_time: float
    end_time: float
    original_text: str
    translated_text: str
    target_language: str
    source_language: Optional[str] = None
    confidence: float = 0.0
    is_final: bool = True


class Meeting(BaseModel):
    """Meeting entity."""
    id: Optional[str] = None
    platform: str
    platform_meeting_id: Optional[str] = None
    title: Optional[str] = None
    organizer: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: List[Speaker] = []
    status: TranslationStatus = TranslationStatus.PENDING


class TranslationJob(BaseModel):
    """Translation job for tracking multi-language output."""
    id: Optional[str] = None
    meeting_id: str
    target_language: str
    segments: List[TranscriptSegment] = []
    status: TranslationStatus = TranslationStatus.PENDING


class ExportFormat(str, Enum):
    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"
    SRT = "srt"
    VTT = "vtt"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "md"