"""
Pydantic schemas for Voice Profile API.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VoiceProfileBase(BaseModel):
    """Base schema for VoiceProfile."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class VoiceProfileCreate(VoiceProfileBase):
    """Schema for creating a voice profile."""

    elevenlabs_voice_id: str = Field(..., description="ElevenLabs voice ID")
    sample_audio_urls: Optional[list[str]] = Field(default_factory=list)


class VoiceProfileUpdate(BaseModel):
    """Schema for updating a voice profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class VoiceProfileResponse(VoiceProfileBase):
    """Schema for voice profile response."""

    id: UUID
    elevenlabs_voice_id: str
    sample_audio_urls: list[str]
    is_active: bool
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VoiceCloneRequest(BaseModel):
    """Schema for voice cloning request."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    # Audio files will be uploaded via multipart/form-data


class VoiceTestRequest(BaseModel):
    """Schema for testing a voice."""

    text: str = Field(..., min_length=1, max_length=1000)
    voice_id: Optional[UUID] = Field(None, description="Voice profile ID (optional)")


class VoiceTestResponse(BaseModel):
    """Schema for voice test response."""

    audio_url: str = Field(..., description="URL to the generated audio")
    duration_seconds: Optional[float] = None
