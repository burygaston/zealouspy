"""Cryptographic utilities for password hashing, tokens, and API keys.

Provides secure password hashing using PBKDF2, token generation, API key
management, and basic encryption utilities.
"""

import hashlib
import secrets
import base64
from typing import Tuple


def hash_password(password: str, salt: bytes = None) -> Tuple[str, str]:
    """Hash a password using PBKDF2-HMAC-SHA256 with salt.

    Generates a cryptographically secure salt if not provided. Uses 100,000
    iterations for resistance against brute-force attacks.

    Args:
        password: Plain text password to hash.
        salt: Optional salt bytes. If None, a random 32-byte salt is generated.

    Returns:
        Tuple of (hashed_password, salt) both as base64-encoded strings.
    """
    if salt is None:
        salt = secrets.token_bytes(32)

    # Use PBKDF2 with SHA-256
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,  # iterations
        dklen=32,
    )

    return base64.b64encode(key).decode('utf-8'), base64.b64encode(salt).decode('utf-8')


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its stored hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        password: Plain text password to verify.
        hashed: Base64-encoded hash to compare against.
        salt: Base64-encoded salt used in the original hash.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    salt_bytes = base64.b64decode(salt.encode('utf-8'))
    new_hash, _ = hash_password(password, salt_bytes)
    return secrets.compare_digest(new_hash, hashed)


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Suitable for session tokens, CSRF tokens, or other security tokens.
    Uses URL-safe base64 encoding.

    Args:
        length: Number of random bytes to generate (default: 32).

    Returns:
        URL-safe base64-encoded token string.
    """
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate a prefixed API key for external API access.

    Format: zls_<32_hex_characters>

    Returns:
        API key string with 'zls_' prefix.
    """
    prefix = "zls"  # zealous
    random_part = secrets.token_hex(16)
    return f"{prefix}_{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage.

    API keys should be hashed before storing in the database, similar to
    passwords.

    Args:
        api_key: API key string to hash.

    Returns:
        SHA-256 hash of the API key as a hexadecimal string.
    """
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code.

    Suitable for 2FA codes, email verification, or SMS verification.

    Args:
        length: Number of digits in the code (default: 6).

    Returns:
        String of random digits.
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def encrypt_data(data: str, key: bytes) -> bytes:
    """Encrypt data using XOR cipher (demo purposes only).

    WARNING: XOR encryption is NOT secure for production use. This is provided
    for demonstration and testing purposes only. Use a proper encryption
    library like cryptography.fernet for production.

    Args:
        data: String data to encrypt.
        key: Encryption key bytes.

    Returns:
        Base64-encoded encrypted data.
    """
    data_bytes = data.encode('utf-8')
    key_extended = (key * (len(data_bytes) // len(key) + 1))[:len(data_bytes)]
    encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_extended))
    return base64.b64encode(encrypted)


def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """Decrypt XOR-encrypted data (demo purposes only).

    WARNING: XOR encryption is NOT secure for production use. This is provided
    for demonstration and testing purposes only.

    Args:
        encrypted_data: Base64-encoded encrypted data.
        key: Decryption key bytes (must match encryption key).

    Returns:
        Decrypted string data.
    """
    data_bytes = base64.b64decode(encrypted_data)
    key_extended = (key * (len(data_bytes) // len(key) + 1))[:len(data_bytes)]
    decrypted = bytes(a ^ b for a, b in zip(data_bytes, key_extended))
    return decrypted.decode('utf-8')
