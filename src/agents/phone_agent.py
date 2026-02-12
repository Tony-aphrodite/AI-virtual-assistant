"""
Phone agent for handling phone conversations with AI.
"""

from typing import Optional

from src.core.logging import get_logger
from src.services.ai.openai_service import get_openai_service

logger = get_logger(__name__)


class PhoneAgent:
    """
    AI agent for phone conversations.
    Handles natural language understanding and response generation.
    """

    def __init__(self) -> None:
        """Initialize phone agent."""
        self.openai = get_openai_service()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt for the agent."""
        return """Eres un asistente virtual profesional para una empresa.

Tu función:
- Responder llamadas telefónicas de manera profesional y amigable
- Ayudar a los clientes con sus consultas
- Agendar citas y reuniones
- Buscar información cuando sea necesario
- Tomar mensajes cuando sea apropiado

Personalidad: Profesional, amigable, eficiente

Reglas importantes:
- Siempre confirma detalles importantes (nombres, fechas, horas)
- Si no estás seguro, pide aclaración
- Nunca inventes información
- Ofrece tomar un mensaje si no puedes ayudar
- Mantén las respuestas concisas y claras
- Habla en español de manera natural y profesional
"""

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        context: Optional[dict] = None,
    ) -> str:
        """
        Generate AI response to user input.

        Args:
            user_message: User's message
            conversation_history: Previous messages in the conversation
            context: Additional context (caller info, business data, etc.)

        Returns:
            AI-generated response
        """
        try:
            # Build messages for GPT-4
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add context if available
            if context:
                context_str = self._format_context(context)
                messages.append({
                    "role": "system",
                    "content": f"Contexto adicional: {context_str}"
                })

            # Add user message
            messages.append({"role": "user", "content": user_message})

            logger.info(
                "Generating agent response",
                user_message_preview=user_message[:100],
                history_length=len(conversation_history or []),
            )

            # Generate response
            response = await self.openai.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=500,  # Keep responses concise for phone calls
            )

            logger.info(
                "Agent response generated",
                response_preview=response[:100] if isinstance(response, str) else "streaming",
            )

            return response if isinstance(response, str) else ""

        except Exception as e:
            logger.error("Failed to generate response", error=str(e))
            # Fallback response
            return "Disculpa, tuve un problema técnico. ¿Podrías repetir lo que dijiste?"

    def _format_context(self, context: dict) -> str:
        """Format context dictionary for prompt."""
        parts = []

        if "caller_name" in context:
            parts.append(f"Nombre del llamante: {context['caller_name']}")

        if "caller_number" in context:
            parts.append(f"Número: {context['caller_number']}")

        if "business_hours" in context:
            parts.append(f"Horario de atención: {context['business_hours']}")

        if "company_name" in context:
            parts.append(f"Empresa: {context['company_name']}")

        return ", ".join(parts) if parts else "No hay contexto adicional"

    async def analyze_intent(self, message: str) -> dict:
        """
        Analyze user intent from message.

        Args:
            message: User message

        Returns:
            Intent analysis with classification and entities
        """
        return await self.openai.detect_intent(message)

    async def analyze_sentiment(self, message: str) -> dict:
        """
        Analyze sentiment of user message.

        Args:
            message: User message

        Returns:
            Sentiment analysis result
        """
        return await self.openai.analyze_sentiment(message)


# Global agent instance
_phone_agent: Optional[PhoneAgent] = None


def get_phone_agent() -> PhoneAgent:
    """
    Get or create phone agent instance (singleton).

    Returns:
        PhoneAgent instance
    """
    global _phone_agent

    if _phone_agent is None:
        _phone_agent = PhoneAgent()

    return _phone_agent
