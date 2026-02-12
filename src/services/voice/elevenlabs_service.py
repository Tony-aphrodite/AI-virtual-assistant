"""
ElevenLabs service for voice cloning and text-to-speech.
"""

import asyncio
from pathlib import Path
from typing import Optional

from elevenlabs import Voice, VoiceSettings, generate, clone, voices

from src.config import settings
from src.core.exceptions import ElevenLabsError, VoiceCloningError
from src.core.logging import get_logger

logger = get_logger(__name__)


class ElevenLabsService:
    """Service for interacting with ElevenLabs API."""

    def __init__(self) -> None:
        """Initialize ElevenLabs service."""
        if not settings.elevenlabs_api_key:
            raise ElevenLabsError(
                "ElevenLabs API key not configured",
                details={"api_key_present": False},
            )

        # Set API key globally for elevenlabs library
        import os
        os.environ["ELEVEN_API_KEY"] = settings.elevenlabs_api_key

        self.default_voice_id = settings.elevenlabs_default_voice_id
        logger.info("ElevenLabs service initialized")

    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (defaults to configured voice)
            model: Model to use (defaults to configured model)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)

        Returns:
            Audio bytes (MP3 format)

        Raises:
            ElevenLabsError: If TTS fails
        """
        try:
            voice_to_use = voice_id or self.default_voice_id
            model_to_use = model or settings.elevenlabs_model

            if not voice_to_use:
                raise ElevenLabsError("No voice ID provided or configured")

            logger.info(
                "Generating speech",
                text_length=len(text),
                voice_id=voice_to_use,
                model=model_to_use,
            )

            # Run in thread pool to avoid blocking
            audio = await asyncio.to_thread(
                generate,
                text=text,
                voice=Voice(
                    voice_id=voice_to_use,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost,
                    ),
                ),
                model=model_to_use,
            )

            logger.info("Speech generated successfully", audio_size=len(audio))
            return audio

        except Exception as e:
            logger.error("Failed to generate speech", error=str(e), text_preview=text[:50])
            raise ElevenLabsError(f"Text-to-speech failed: {str(e)}")

    async def clone_voice(
        self,
        name: str,
        audio_files: list[Path],
        description: Optional[str] = None,
    ) -> str:
        """
        Clone a voice from audio samples.

        Args:
            name: Name for the cloned voice
            audio_files: List of audio file paths (MP3/WAV, at least 1 minute total)
            description: Optional description

        Returns:
            Voice ID of the cloned voice

        Raises:
            VoiceCloningError: If cloning fails
        """
        try:
            if len(audio_files) == 0:
                raise VoiceCloningError("At least one audio file is required")

            logger.info(
                "Cloning voice",
                name=name,
                num_samples=len(audio_files),
            )

            # Convert Path objects to strings
            audio_paths = [str(path) for path in audio_files]

            # Run in thread pool
            voice = await asyncio.to_thread(
                clone,
                name=name,
                description=description or f"Cloned voice: {name}",
                files=audio_paths,
            )

            logger.info("Voice cloned successfully", voice_id=voice.voice_id, name=name)
            return voice.voice_id

        except Exception as e:
            logger.error("Failed to clone voice", error=str(e), name=name)
            raise VoiceCloningError(f"Voice cloning failed: {str(e)}")

    async def list_voices(self) -> list[dict]:
        """
        List all available voices.

        Returns:
            List of voice dictionaries

        Raises:
            ElevenLabsError: If listing fails
        """
        try:
            logger.info("Listing available voices")

            # Run in thread pool
            voice_list = await asyncio.to_thread(voices)

            results = [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, "category", None),
                    "description": getattr(voice, "description", None),
                }
                for voice in voice_list
            ]

            logger.info("Voices listed successfully", count=len(results))
            return results

        except Exception as e:
            logger.error("Failed to list voices", error=str(e))
            raise ElevenLabsError(f"Failed to list voices: {str(e)}")

    async def get_voice(self, voice_id: str) -> dict:
        """
        Get details for a specific voice.

        Args:
            voice_id: Voice ID

        Returns:
            Voice details dictionary

        Raises:
            ElevenLabsError: If voice not found
        """
        try:
            voice_list = await self.list_voices()
            voice = next((v for v in voice_list if v["voice_id"] == voice_id), None)

            if not voice:
                raise ElevenLabsError(
                    f"Voice not found: {voice_id}",
                    details={"voice_id": voice_id},
                )

            return voice

        except Exception as e:
            logger.error("Failed to get voice", error=str(e), voice_id=voice_id)
            raise ElevenLabsError(f"Failed to get voice: {str(e)}")

    async def delete_voice(self, voice_id: str) -> None:
        """
        Delete a cloned voice.

        Args:
            voice_id: Voice ID to delete

        Raises:
            ElevenLabsError: If deletion fails
        """
        try:
            from elevenlabs import delete_voice

            logger.info("Deleting voice", voice_id=voice_id)

            await asyncio.to_thread(delete_voice, voice_id)

            logger.info("Voice deleted successfully", voice_id=voice_id)

        except Exception as e:
            logger.error("Failed to delete voice", error=str(e), voice_id=voice_id)
            raise ElevenLabsError(f"Failed to delete voice: {str(e)}")


# Global service instance
_elevenlabs_service: Optional[ElevenLabsService] = None


def get_elevenlabs_service() -> ElevenLabsService:
    """
    Get or create ElevenLabs service instance (singleton).

    Returns:
        ElevenLabsService instance
    """
    global _elevenlabs_service

    if _elevenlabs_service is None:
        _elevenlabs_service = ElevenLabsService()

    return _elevenlabs_service
