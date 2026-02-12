"""
OpenAI service for GPT-4 conversations and Whisper transcription.
"""

import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional

from openai import AsyncOpenAI, OpenAIError as OpenAISDKError

from src.config import settings
from src.core.exceptions import OpenAIError, TranscriptionError
from src.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(self) -> None:
        """Initialize OpenAI client."""
        if not settings.openai_api_key:
            raise OpenAIError(
                "OpenAI API key not configured",
                details={"api_key_present": False},
            )

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

        logger.info("OpenAI service initialized", model=self.model)

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """
        Generate a chat completion using GPT-4.

        Args:
            messages: List of messages in OpenAI format
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature (defaults to configured temperature)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response

        Returns:
            Generated response text (or async iterator if streaming)

        Raises:
            OpenAIError: If completion fails
        """
        try:
            model_to_use = model or self.model
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens or self.max_tokens

            logger.info(
                "Generating chat completion",
                model=model_to_use,
                num_messages=len(messages),
                temperature=temp,
            )

            if stream:
                return self._stream_completion(
                    messages, model_to_use, temp, tokens
                )

            response = await self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
            )

            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            logger.info(
                "Chat completion generated",
                response_length=len(content),
                tokens_used=tokens_used,
            )

            return content

        except OpenAISDKError as e:
            logger.error("OpenAI API error", error=str(e), messages_count=len(messages))
            raise OpenAIError(f"Chat completion failed: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error", error=str(e))
            raise OpenAIError(f"Unexpected error: {str(e)}")

    async def _stream_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Stream chat completion chunks."""
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error("Streaming error", error=str(e))
            raise OpenAIError(f"Streaming failed: {str(e)}")

    async def transcribe_audio(
        self,
        audio_file: Path | bytes,
        language: Optional[str] = "es",
        prompt: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio using Whisper.

        Args:
            audio_file: Path to audio file or audio bytes
            language: Language code (e.g., 'es' for Spanish, 'en' for English)
            prompt: Optional prompt to guide transcription

        Returns:
            Transcribed text

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            logger.info(
                "Transcribing audio",
                audio_type=type(audio_file).__name__,
                language=language,
            )

            # Handle both file paths and bytes
            if isinstance(audio_file, bytes):
                # Create a temporary file-like object
                import io
                audio_data = io.BytesIO(audio_file)
                audio_data.name = "audio.mp3"  # Required by OpenAI API
            else:
                audio_data = open(audio_file, "rb")

            try:
                response = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data,
                    language=language,
                    prompt=prompt,
                )

                text = response.text

                logger.info(
                    "Audio transcribed successfully",
                    text_length=len(text),
                    text_preview=text[:100],
                )

                return text

            finally:
                if hasattr(audio_data, "close"):
                    audio_data.close()

        except OpenAISDKError as e:
            logger.error("Whisper API error", error=str(e))
            raise TranscriptionError(f"Transcription failed: {str(e)}")
        except Exception as e:
            logger.error("Unexpected transcription error", error=str(e))
            raise TranscriptionError(f"Unexpected error: {str(e)}")

    async def analyze_sentiment(self, text: str) -> dict[str, any]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis result with sentiment and confidence

        Raises:
            OpenAIError: If analysis fails
        """
        try:
            prompt = f"""Analyze the sentiment of the following text and provide:
1. Overall sentiment (positive, negative, or neutral)
2. Confidence score (0.0 to 1.0)
3. Key emotions detected

Text: "{text}"

Respond in JSON format:
{{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "emotions": ["emotion1", "emotion2"]}}
"""

            messages = [
                {"role": "system", "content": "You are a sentiment analysis expert."},
                {"role": "user", "content": prompt},
            ]

            response = await self.chat_completion(messages, temperature=0.0)

            # Parse JSON response
            import json
            result = json.loads(response)

            logger.info("Sentiment analyzed", sentiment=result.get("sentiment"))
            return result

        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))
            # Return neutral sentiment on failure
            return {"sentiment": "neutral", "confidence": 0.5, "emotions": []}

    async def detect_intent(self, text: str) -> dict[str, any]:
        """
        Detect intent from user input.

        Args:
            text: User input text

        Returns:
            Intent detection result

        Raises:
            OpenAIError: If detection fails
        """
        try:
            prompt = f"""Detect the intent of the following user message:

Message: "{text}"

Classify into one of these intents:
- information_request: User wants information
- appointment_scheduling: User wants to schedule or modify an appointment
- complaint: User has a complaint or issue
- general_inquiry: General question
- greeting: Greeting or small talk
- other: None of the above

Respond in JSON format:
{{"intent": "intent_name", "confidence": 0.0-1.0, "entities": {{}}, "summary": "brief summary"}}
"""

            messages = [
                {"role": "system", "content": "You are an intent classification expert."},
                {"role": "user", "content": prompt},
            ]

            response = await self.chat_completion(messages, temperature=0.0)

            # Parse JSON response
            import json
            result = json.loads(response)

            logger.info("Intent detected", intent=result.get("intent"))
            return result

        except Exception as e:
            logger.error("Intent detection failed", error=str(e))
            # Return unknown intent on failure
            return {
                "intent": "other",
                "confidence": 0.0,
                "entities": {},
                "summary": text[:100],
            }

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to count tokens for
            model: Model name (for accurate counting)

        Returns:
            Estimated token count
        """
        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model(model or self.model)
            return len(encoding.encode(text))

        except Exception:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4


# Global service instance
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """
    Get or create OpenAI service instance (singleton).

    Returns:
        OpenAIService instance
    """
    global _openai_service

    if _openai_service is None:
        _openai_service = OpenAIService()

    return _openai_service
