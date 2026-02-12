"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", description="Environment name")

    # Application
    app_name: str = Field(default="AI Virtual Assistant", description="Application name")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    secret_key: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for encryption",
    )
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/ai_assistant",
        description="PostgreSQL connection URL",
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(
        default=0, description="Maximum overflow connections"
    )

    # Redis
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=50, description="Maximum Redis connections")

    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4-0125-preview", description="OpenAI model to use"
    )
    openai_max_tokens: int = Field(
        default=4000, description="Maximum tokens for OpenAI responses"
    )
    openai_temperature: float = Field(
        default=0.7, description="Temperature for OpenAI responses"
    )

    # Twilio
    twilio_account_sid: str = Field(default="", description="Twilio Account SID")
    twilio_auth_token: str = Field(default="", description="Twilio Auth Token")
    twilio_phone_number: str = Field(default="", description="Twilio phone number")
    twilio_webhook_url: Optional[str] = Field(
        default=None, description="Public webhook URL for Twilio"
    )

    # ElevenLabs
    elevenlabs_api_key: str = Field(default="", description="ElevenLabs API key")
    elevenlabs_default_voice_id: Optional[str] = Field(
        default=None, description="Default ElevenLabs voice ID"
    )
    elevenlabs_model: str = Field(
        default="eleven_multilingual_v2", description="ElevenLabs model"
    )

    # WhatsApp (future)
    whatsapp_phone_number_id: Optional[str] = Field(
        default=None, description="WhatsApp phone number ID"
    )
    whatsapp_access_token: Optional[str] = Field(
        default=None, description="WhatsApp access token"
    )

    # Google APIs (future)
    google_client_id: Optional[str] = Field(default=None, description="Google client ID")
    google_client_secret: Optional[str] = Field(
        default=None, description="Google client secret"
    )
    google_refresh_token: Optional[str] = Field(
        default=None, description="Google refresh token"
    )

    # SerpAPI (future)
    serpapi_api_key: Optional[str] = Field(default=None, description="SerpAPI key")

    # Celery
    celery_broker_url: RedisDsn = Field(
        default="redis://localhost:6379/1", description="Celery broker URL"
    )
    celery_result_backend: RedisDsn = Field(
        default="redis://localhost:6379/2", description="Celery result backend URL"
    )

    # Storage
    audio_storage_path: str = Field(
        default="/app/storage/audio", description="Path for audio file storage"
    )
    max_audio_size_mb: int = Field(
        default=10, description="Maximum audio file size in MB"
    )

    # Security
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials")
    cors_allow_methods: list[str] = Field(
        default=["*"], description="Allowed HTTP methods"
    )
    cors_allow_headers: list[str] = Field(
        default=["*"], description="Allowed HTTP headers"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100, description="Maximum requests per time window"
    )
    rate_limit_window: int = Field(default=60, description="Time window in seconds")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to create singleton pattern for settings.
    """
    return Settings()


# Global settings instance
settings = get_settings()
