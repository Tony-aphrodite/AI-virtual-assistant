"""
Pydantic schemas for Webhook payloads.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TwilioVoiceWebhook(BaseModel):
    """Schema for Twilio voice webhook payload."""

    CallSid: str = Field(..., description="Unique identifier for the call")
    AccountSid: str = Field(..., description="Twilio account SID")
    From: str = Field(..., description="Caller's phone number")
    To: str = Field(..., description="Recipient's phone number")
    CallStatus: str = Field(..., description="Current call status")
    Direction: str = Field(..., description="Call direction (inbound/outbound)")
    ApiVersion: Optional[str] = None
    ForwardedFrom: Optional[str] = None
    CallerName: Optional[str] = None


class TwilioStatusCallback(BaseModel):
    """Schema for Twilio status callback."""

    CallSid: str
    CallStatus: str
    CallDuration: Optional[str] = None
    RecordingUrl: Optional[str] = None
    RecordingSid: Optional[str] = None
    RecordingDuration: Optional[str] = None


class TwilioRecordingCallback(BaseModel):
    """Schema for Twilio recording callback."""

    CallSid: str
    RecordingSid: str
    RecordingUrl: str
    RecordingStatus: str
    RecordingDuration: str
    RecordingChannels: Optional[str] = None
    RecordingSource: Optional[str] = None


class TwilioGatherCallback(BaseModel):
    """Schema for Twilio gather (speech input) callback."""

    CallSid: str
    SpeechResult: Optional[str] = Field(None, description="Transcribed speech")
    Confidence: Optional[str] = Field(None, description="Confidence score")
    UnstableSpeechResult: Optional[str] = None
