"""
Security utilities for authentication, encryption, and webhook validation.
"""

import hashlib
import hmac
from typing import Optional
from urllib.parse import urlencode

from passlib.context import CryptContext

from src.config import settings
from src.core.exceptions import AuthenticationError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_twilio_signature(
    url: str,
    params: dict[str, str],
    signature: str,
    auth_token: Optional[str] = None,
) -> bool:
    """
    Validate Twilio webhook signature to ensure request authenticity.

    Args:
        url: The full URL of the webhook (including protocol and hostname)
        params: Dictionary of POST parameters from the request
        signature: X-Twilio-Signature header value
        auth_token: Twilio auth token (defaults to settings.twilio_auth_token)

    Returns:
        True if signature is valid, False otherwise

    Raises:
        AuthenticationError: If auth_token is not provided or configured
    """
    token = auth_token or settings.twilio_auth_token
    if not token:
        raise AuthenticationError(
            "Twilio auth token not configured",
            code="TWILIO_AUTH_TOKEN_MISSING",
        )

    # Sort parameters and concatenate with URL
    data = url + urlencode(sorted(params.items()))

    # Compute HMAC-SHA1 signature
    computed_signature = hmac.new(
        token.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha1,
    ).digest()

    # Encode to base64
    import base64
    computed_signature_b64 = base64.b64encode(computed_signature).decode()

    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(computed_signature_b64, signature)


def validate_whatsapp_signature(
    payload: bytes,
    signature: str,
    app_secret: Optional[str] = None,
) -> bool:
    """
    Validate WhatsApp webhook signature.

    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value (format: sha256=<hash>)
        app_secret: WhatsApp app secret (defaults to settings.secret_key)

    Returns:
        True if signature is valid, False otherwise
    """
    secret = app_secret or settings.secret_key
    if not secret:
        raise AuthenticationError(
            "WhatsApp app secret not configured",
            code="WHATSAPP_SECRET_MISSING",
        )

    # Remove 'sha256=' prefix if present
    if signature.startswith("sha256="):
        signature = signature[7:]

    # Compute HMAC-SHA256 signature
    computed_signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(computed_signature, signature)


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        64-character hexadecimal API key
    """
    import secrets
    return secrets.token_hex(32)


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    Mask sensitive data, showing only first N and last N characters.

    Args:
        data: Sensitive string to mask
        show_chars: Number of characters to show at start and end

    Returns:
        Masked string

    Example:
        >>> mask_sensitive_data("sk-1234567890abcdef", show_chars=4)
        "sk-1...cdef"
    """
    if len(data) <= show_chars * 2:
        return "*" * len(data)

    return f"{data[:show_chars]}...{data[-show_chars:]}"
