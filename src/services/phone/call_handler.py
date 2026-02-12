"""
Call handler for orchestrating the complete call flow.
Integrates Twilio, OpenAI, and ElevenLabs services.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.phone_agent import get_phone_agent
from src.core.logging import get_logger
from src.models.call import Call, CallStatus
from src.models.conversation import Conversation
from src.models.voice_profile import VoiceProfile
from src.services.ai.openai_service import get_openai_service
from src.services.phone.twilio_service import get_twilio_service
from src.services.voice.elevenlabs_service import get_elevenlabs_service

logger = get_logger(__name__)


class CallHandler:
    """Orchestrates the complete phone call workflow."""

    def __init__(self) -> None:
        """Initialize call handler with all services."""
        self.twilio = get_twilio_service()
        self.openai = get_openai_service()
        self.elevenlabs = get_elevenlabs_service()
        self.phone_agent = get_phone_agent()

    async def handle_incoming_call(
        self,
        call_sid: str,
        from_number: str,
        to_number: str,
        db: AsyncSession,
    ) -> str:
        """
        Handle incoming call and return initial TwiML.

        Args:
            call_sid: Twilio call SID
            from_number: Caller's number
            to_number: Called number
            db: Database session

        Returns:
            TwiML response string
        """
        try:
            logger.info(
                "Handling incoming call",
                call_sid=call_sid,
                from_number=from_number,
            )

            # Create call record
            call = Call(
                twilio_call_sid=call_sid,
                direction="inbound",
                from_number=from_number,
                to_number=to_number,
                status=CallStatus.IN_PROGRESS,
            )
            db.add(call)
            await db.commit()

            # Create conversation record
            conversation = Conversation(
                call_id=call.id,
                messages=[],
            )
            db.add(conversation)
            await db.commit()

            # Generate greeting TwiML
            greeting = "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            twiml = self.twilio.generate_greeting_twiml(greeting)

            logger.info("Initial TwiML generated", call_id=call.id)
            return twiml

        except Exception as e:
            logger.error("Failed to handle incoming call", error=str(e))
            # Return fallback TwiML
            return self.twilio.generate_hangup_twiml(
                "Lo siento, hay un problema técnico. Por favor, llama más tarde."
            )

    async def handle_user_speech(
        self,
        call_sid: str,
        speech_result: str,
        db: AsyncSession,
    ) -> str:
        """
        Handle user speech input and generate AI response.

        Args:
            call_sid: Twilio call SID
            speech_result: Transcribed user speech
            db: Database session

        Returns:
            TwiML response string
        """
        try:
            logger.info(
                "Handling user speech",
                call_sid=call_sid,
                speech_preview=speech_result[:100],
            )

            # Get call and conversation from database
            call_query = await db.execute(
                select(Call).where(Call.twilio_call_sid == call_sid)
            )
            call = call_query.scalar_one_or_none()

            if not call:
                logger.error("Call not found", call_sid=call_sid)
                return self.twilio.generate_hangup_twiml()

            conv_query = await db.execute(
                select(Conversation).where(Conversation.call_id == call.id)
            )
            conversation = conv_query.scalar_one_or_none()

            if not conversation:
                logger.error("Conversation not found", call_id=call.id)
                return self.twilio.generate_hangup_twiml()

            # Add user message to conversation
            conversation.add_message("user", speech_result)

            # Generate AI response
            ai_response = await self.phone_agent.generate_response(
                user_message=speech_result,
                conversation_history=conversation.get_messages_for_llm(),
                context={
                    "caller_number": call.from_number,
                    "company_name": "Tu Empresa",
                },
            )

            # Add AI response to conversation
            conversation.add_message("assistant", ai_response)

            # Analyze intent and sentiment (async, don't block)
            try:
                intent_result = await self.phone_agent.analyze_intent(speech_result)
                conversation.intent = intent_result.get("intent")

                sentiment_result = await self.phone_agent.analyze_sentiment(speech_result)
                conversation.sentiment = sentiment_result.get("sentiment")
            except Exception as e:
                logger.warning("Failed to analyze intent/sentiment", error=str(e))

            await db.commit()

            # Convert AI response to speech
            voice_profile = await self._get_active_voice_profile(db)
            audio_bytes = await self.elevenlabs.text_to_speech(
                text=ai_response,
                voice_id=voice_profile.elevenlabs_voice_id if voice_profile else None,
            )

            # Save audio and get URL (simplified - in production, use proper storage)
            audio_url = await self._save_audio(audio_bytes, call_sid)

            # Generate TwiML with AI response
            twiml = self.twilio.generate_response_twiml(
                message=ai_response,
                audio_url=audio_url,
                continue_conversation=True,
            )

            logger.info("Response TwiML generated", call_id=call.id)
            return twiml

        except Exception as e:
            logger.error("Failed to handle user speech", error=str(e))
            return self.twilio.generate_response_twiml(
                message="Disculpa, tuve un problema. ¿Puedes repetir?",
                continue_conversation=True,
            )

    async def handle_call_completed(
        self,
        call_sid: str,
        duration: Optional[int],
        recording_url: Optional[str],
        db: AsyncSession,
    ) -> None:
        """
        Handle call completion and update records.

        Args:
            call_sid: Twilio call SID
            duration: Call duration in seconds
            recording_url: URL to call recording
            db: Database session
        """
        try:
            logger.info("Handling call completion", call_sid=call_sid)

            call_query = await db.execute(
                select(Call).where(Call.twilio_call_sid == call_sid)
            )
            call = call_query.scalar_one_or_none()

            if call:
                call.status = CallStatus.COMPLETED
                call.duration = duration
                call.recording_url = recording_url

                # Generate conversation summary
                conv_query = await db.execute(
                    select(Conversation).where(Conversation.call_id == call.id)
                )
                conversation = conv_query.scalar_one_or_none()

                if conversation and conversation.messages:
                    summary = await self._generate_summary(conversation.messages)
                    conversation.summary = summary

                await db.commit()

                logger.info("Call completed and updated", call_id=call.id)

        except Exception as e:
            logger.error("Failed to handle call completion", error=str(e))

    async def _get_active_voice_profile(self, db: AsyncSession) -> Optional[VoiceProfile]:
        """Get active voice profile for TTS."""
        try:
            result = await db.execute(
                select(VoiceProfile)
                .where(VoiceProfile.is_active == True)
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None

    async def _save_audio(self, audio_bytes: bytes, call_sid: str) -> str:
        """Save audio to storage and return URL."""
        # Simplified - in production, upload to S3/Cloud Storage
        # For now, return a placeholder
        return f"https://storage.example.com/audio/{call_sid}.mp3"

    async def _generate_summary(self, messages: list[dict]) -> str:
        """Generate conversation summary."""
        try:
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in messages
            ])

            prompt = f"""Resume esta conversación telefónica en 2-3 oraciones:

{conversation_text}

Resume:"""

            summary = await self.openai.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,
            )

            return summary if isinstance(summary, str) else ""

        except Exception as e:
            logger.error("Failed to generate summary", error=str(e))
            return "Resumen no disponible"


# Global handler instance
_call_handler: Optional[CallHandler] = None


def get_call_handler() -> CallHandler:
    """
    Get or create call handler instance (singleton).

    Returns:
        CallHandler instance
    """
    global _call_handler

    if _call_handler is None:
        _call_handler = CallHandler()

    return _call_handler
