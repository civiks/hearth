"""Symmetric encryption for sensitive per-user secrets (BYOK Gemini keys).

Why Fernet: ships in `cryptography`, AEAD (AES-128-CBC + HMAC), URL-safe
tokens, no manual nonce/IV handling. Overkill it isn't — under it.

The Fernet key lives in `settings.gemini_key_encryption_key` (env
`GEMINI_KEY_ENCRYPTION_KEY`). Rotating it invalidates every stored key —
users would need to re-paste theirs. Acceptable for our scale; if that
changes, layer key versioning on top.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from backend.core.config import get_settings


class EncryptionUnavailable(RuntimeError):
    """Raised when `GEMINI_KEY_ENCRYPTION_KEY` isn't configured."""


def _cipher() -> Fernet:
    raw = get_settings().gemini_key_encryption_key.strip()
    if not raw:
        raise EncryptionUnavailable(
            "GEMINI_KEY_ENCRYPTION_KEY is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    try:
        return Fernet(raw.encode())
    except (ValueError, TypeError) as e:
        raise EncryptionUnavailable(
            "GEMINI_KEY_ENCRYPTION_KEY is not a valid Fernet key (must be a "
            "url-safe base64-encoded 32-byte value)."
        ) from e


def encrypt(plaintext: str) -> str:
    """Encrypt and return a UTF-8 token suitable for storing in a TEXT column."""
    return _cipher().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(token: str) -> str:
    """Decrypt a token produced by `encrypt`. Raises InvalidToken on tamper/wrong-key."""
    try:
        return _cipher().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        # Surface as the same exception so callers handle one type — they
        # treat it as "stored key is unusable; ask the user to re-paste."
        raise
