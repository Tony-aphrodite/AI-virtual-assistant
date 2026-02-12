"""
Custom exception classes for the AI Virtual Assistant application.
Provides specific exception types for different error scenarios.
"""

from typing import Any, Optional


class AIAssistantException(Exception):
    """Base exception for all AI Assistant errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(AIAssistantException):
    """Raised when there's a configuration error."""

    pass


class DatabaseError(AIAssistantException):
    """Raised when there's a database operation error."""

    pass


class ExternalAPIError(AIAssistantException):
    """Base class for external API errors."""

    def __init__(
        self,
        message: str,
        service: str,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.service = service
        self.status_code = status_code
        super().__init__(
            message,
            code=f"{service.upper()}_API_ERROR",
            details={**(details or {}), "service": service, "status_code": status_code},
        )


class OpenAIError(ExternalAPIError):
    """Raised when OpenAI API call fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, service="openai", **kwargs)


class TwilioError(ExternalAPIError):
    """Raised when Twilio API call fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, service="twilio", **kwargs)


class ElevenLabsError(ExternalAPIError):
    """Raised when ElevenLabs API call fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, service="elevenlabs", **kwargs)


class WhatsAppError(ExternalAPIError):
    """Raised when WhatsApp API call fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, service="whatsapp", **kwargs)


class GoogleAPIError(ExternalAPIError):
    """Raised when Google API call fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, service="google", **kwargs)


class SerpAPIError(ExternalAPIError):
    """Raised when SerpAPI call fails."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, service="serpapi", **kwargs)


class VoiceProcessingError(AIAssistantException):
    """Raised when voice processing fails."""

    pass


class TranscriptionError(VoiceProcessingError):
    """Raised when audio transcription fails."""

    pass


class TextToSpeechError(VoiceProcessingError):
    """Raised when text-to-speech conversion fails."""

    pass


class VoiceCloningError(VoiceProcessingError):
    """Raised when voice cloning fails."""

    pass


class AudioProcessingError(VoiceProcessingError):
    """Raised when audio file processing fails."""

    pass


class CallHandlingError(AIAssistantException):
    """Raised when call handling fails."""

    pass


class ConversationError(AIAssistantException):
    """Raised when conversation management fails."""

    pass


class AgentError(AIAssistantException):
    """Raised when an AI agent encounters an error."""

    pass


class ValidationError(AIAssistantException):
    """Raised when data validation fails."""

    pass


class AuthenticationError(AIAssistantException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(AIAssistantException):
    """Raised when authorization fails."""

    pass


class RateLimitError(AIAssistantException):
    """Raised when rate limit is exceeded."""

    pass


class ResourceNotFoundError(AIAssistantException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str, **kwargs: Any) -> None:
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            message,
            code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class StorageError(AIAssistantException):
    """Raised when file storage operation fails."""

    pass


class CacheError(AIAssistantException):
    """Raised when cache operation fails."""

    pass
