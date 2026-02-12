"""
Voice profile model for storing voice cloning information.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class VoiceProfile(BaseModel):
    """
    Voice profile model for voice cloning.

    Stores information about cloned voices including:
    - ElevenLabs voice ID
    - Profile name and description
    - Training audio sample URLs
    - Active status
    - User association
    """

    __tablename__ = "voice_profiles"

    # Profile information
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ElevenLabs voice ID
    elevenlabs_voice_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    # Training samples (list of URLs)
    sample_audio_urls: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True, default=list
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    # User association (future: multi-tenancy support)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Additional metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    def __repr__(self) -> str:
        return (
            f"VoiceProfile(id={self.id}, name={self.name}, "
            f"elevenlabs_id={self.elevenlabs_voice_id}, active={self.is_active})"
        )
