"""
Pydantic schemas for Call API.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.call import CallDirection, CallStatus


class CallBase(BaseModel):
    """Base schema for Call."""

    from_number: str = Field(..., description="Caller's phone number")
    to_number: str = Field(..., description="Recipient's phone number")


class CallCreate(CallBase):
    """Schema for creating a call."""

    twilio_call_sid: str = Field(..., description="Twilio call SID")
    direction: CallDirection = Field(..., description="Call direction")


class CallUpdate(BaseModel):
    """Schema for updating a call."""

    status: Optional[CallStatus] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcription: Optional[str] = None
    metadata: Optional[dict] = None


class CallResponse(CallBase):
    """Schema for call response."""

    id: UUID
    twilio_call_sid: str
    direction: CallDirection
    status: CallStatus
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcription: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallListResponse(BaseModel):
    """Schema for paginated call list."""

    items: list[CallResponse]
    total: int
    page: int
    page_size: int


class OutboundCallRequest(BaseModel):
    """Schema for initiating an outbound call."""

    to_number: str = Field(..., description="Phone number to call")
    from_number: Optional[str] = Field(None, description="Caller ID (optional)")
    message: Optional[str] = Field(None, description="Initial message to speak")
