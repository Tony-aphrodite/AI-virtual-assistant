"""
Call model for storing phone call records.
"""

import enum
from typing import Optional

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class CallDirection(str, enum.Enum):
    """Call direction enumeration."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(str, enum.Enum):
    """Call status enumeration."""

    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BUSY = "busy"
    FAILED = "failed"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"


class Call(BaseModel):
    """
    Call record model.

    Stores information about phone calls including:
    - Call metadata (direction, numbers, duration)
    - Twilio call SID for external reference
    - Call status and lifecycle
    - Recording and transcription URLs
    - Additional metadata in JSON format
    """

    __tablename__ = "calls"

    # Twilio identifiers
    twilio_call_sid: Mapped[str] = mapped_column(
        String(34), unique=True, nullable=False, index=True
    )

    # Call details
    direction: Mapped[CallDirection] = mapped_column(
        Enum(CallDirection), nullable=False, index=True
    )
    from_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    to_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Call status
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus), nullable=False, default=CallStatus.INITIATED, index=True
    )

    # Duration in seconds
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Recording and transcription
    recording_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcription: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Additional metadata (flexible JSON field)
    call_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="call", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"Call(id={self.id}, sid={self.twilio_call_sid}, "
            f"direction={self.direction}, status={self.status})"
        )
