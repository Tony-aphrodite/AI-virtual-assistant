"""
Pydantic schemas for Conversation API.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """Schema for a single message in a conversation."""

    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO timestamp")


class ConversationBase(BaseModel):
    """Base schema for Conversation."""

    call_id: UUID


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""

    messages: list[dict] = Field(default_factory=list)
    intent: Optional[str] = None
    sentiment: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    messages: Optional[list[dict]] = None
    summary: Optional[str] = None
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    metadata: Optional[dict] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""

    id: UUID
    messages: list[dict]
    summary: Optional[str] = None
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""

    message: str = Field(..., min_length=1, max_length=5000)
    call_sid: Optional[str] = Field(None, description="Associated call SID")
    context: Optional[dict] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Schema for chat response."""

    response: str = Field(..., description="AI-generated response")
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
