"""
Twilio service for phone call handling.
Provides methods for making calls, managing call state, and generating TwiML.
"""

from typing import Optional

from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse

from src.config import settings
from src.core.exceptions import TwilioError
from src.core.logging import get_logger

logger = get_logger(__name__)


class TwilioService:
    """Service for interacting with Twilio API."""

    def __init__(self) -> None:
        """Initialize Twilio client."""
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise TwilioError(
                "Twilio credentials not configured",
                details={
                    "account_sid": bool(settings.twilio_account_sid),
                    "auth_token": bool(settings.twilio_auth_token),
                },
            )

        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number
        logger.info("Twilio service initialized", phone_number=self.phone_number)

    def make_outbound_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> str:
        """
        Initiate an outbound call.

        Args:
            to_number: Phone number to call
            from_number: Caller ID (defaults to configured Twilio number)
            callback_url: Webhook URL for call events

        Returns:
            Twilio call SID

        Raises:
            TwilioError: If call fails
        """
        try:
            from_num = from_number or self.phone_number
            callback = callback_url or f"{settings.twilio_webhook_url}/voice"

            call = self.client.calls.create(
                to=to_number,
                from_=from_num,
                url=callback,
                status_callback=f"{settings.twilio_webhook_url}/status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
            )

            logger.info(
                "Outbound call initiated",
                call_sid=call.sid,
                to_number=to_number,
                from_number=from_num,
            )

            return call.sid

        except Exception as e:
            logger.error("Failed to make outbound call", error=str(e), to_number=to_number)
            raise TwilioError(f"Failed to make call: {str(e)}")

    def generate_greeting_twiml(self, message: Optional[str] = None) -> str:
        """
        Generate TwiML for initial greeting with speech gathering.

        Args:
            message: Custom greeting message (optional)

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        greeting = message or "Hello! I am your AI assistant. How can I help you today?"

        gather = Gather(
            input="speech",
            action=f"{settings.twilio_webhook_url}/gather",
            method="POST",
            speech_timeout="auto",
            language="es-ES",  # Spanish (adjust based on requirements)
        )
        gather.say(greeting, language="es-ES")

        response.append(gather)

        # Fallback if no input
        response.say("I didn't receive any input. Goodbye!", language="es-ES")
        response.hangup()

        return str(response)

    def generate_response_twiml(
        self,
        message: str,
        audio_url: Optional[str] = None,
        continue_conversation: bool = True,
    ) -> str:
        """
        Generate TwiML for AI response.

        Args:
            message: Text message to speak (fallback)
            audio_url: URL to pre-generated audio (preferred)
            continue_conversation: Whether to continue listening

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        if audio_url:
            response.play(audio_url)
        else:
            response.say(message, language="es-ES")

        if continue_conversation:
            gather = Gather(
                input="speech",
                action=f"{settings.twilio_webhook_url}/gather",
                method="POST",
                speech_timeout="auto",
                language="es-ES",
            )
            response.append(gather)
        else:
            response.say("Thank you for calling. Goodbye!", language="es-ES")
            response.hangup()

        return str(response)

    def generate_hangup_twiml(self, message: Optional[str] = None) -> str:
        """
        Generate TwiML to end the call.

        Args:
            message: Goodbye message (optional)

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()

        if message:
            response.say(message, language="es-ES")

        response.hangup()
        return str(response)

    def get_call_details(self, call_sid: str) -> dict:
        """
        Get details for a specific call.

        Args:
            call_sid: Twilio call SID

        Returns:
            Call details dictionary

        Raises:
            TwilioError: If call not found
        """
        try:
            call = self.client.calls(call_sid).fetch()

            return {
                "sid": call.sid,
                "from": call.from_,
                "to": call.to,
                "status": call.status,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "price": call.price,
                "direction": call.direction,
            }

        except Exception as e:
            logger.error("Failed to get call details", error=str(e), call_sid=call_sid)
            raise TwilioError(f"Failed to get call details: {str(e)}")

    def get_call_recordings(self, call_sid: str) -> list[dict]:
        """
        Get recordings for a specific call.

        Args:
            call_sid: Twilio call SID

        Returns:
            List of recording details

        Raises:
            TwilioError: If query fails
        """
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)

            return [
                {
                    "sid": rec.sid,
                    "duration": rec.duration,
                    "url": f"https://api.twilio.com{rec.uri.replace('.json', '.mp3')}",
                    "status": rec.status,
                    "date_created": rec.date_created,
                }
                for rec in recordings
            ]

        except Exception as e:
            logger.error(
                "Failed to get recordings", error=str(e), call_sid=call_sid
            )
            raise TwilioError(f"Failed to get recordings: {str(e)}")

    def download_recording(self, recording_url: str) -> bytes:
        """
        Download a call recording.

        Args:
            recording_url: URL to the recording

        Returns:
            Audio bytes

        Raises:
            TwilioError: If download fails
        """
        try:
            import httpx

            response = httpx.get(
                recording_url,
                auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            )
            response.raise_for_status()

            return response.content

        except Exception as e:
            logger.error("Failed to download recording", error=str(e))
            raise TwilioError(f"Failed to download recording: {str(e)}")


# Global service instance
_twilio_service: Optional[TwilioService] = None


def get_twilio_service() -> TwilioService:
    """
    Get or create Twilio service instance (singleton).

    Returns:
        TwilioService instance
    """
    global _twilio_service

    if _twilio_service is None:
        _twilio_service = TwilioService()

    return _twilio_service
