"""Cryptographic utilities - COMPLETELY UNTESTED."""

import hashlib
import secrets
import base64
from typing import Tuple


def hash_password(password: str, salt: bytes = None) -> Tuple[str, str]:
    """Hash a password with salt."""
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
    """Verify a password against its hash."""
    salt_bytes = base64.b64decode(salt.encode('utf-8'))
    new_hash, _ = hash_password(password, salt_bytes)
    return secrets.compare_digest(new_hash, hashed)


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate an API key."""
    prefix = "zls"  # zealous
    random_part = secrets.token_hex(16)
    return f"{prefix}_{random_part}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def encrypt_data(data: str, key: bytes) -> bytes:
    """Simple XOR encryption (for demo purposes only)."""
    data_bytes = data.encode('utf-8')
    key_extended = (key * (len(data_bytes) // len(key) + 1))[:len(data_bytes)]
    encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_extended))
    return base64.b64encode(encrypted)


def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """Simple XOR decryption (for demo purposes only)."""
    data_bytes = base64.b64decode(encrypted_data)
    key_extended = (key * (len(data_bytes) // len(key) + 1))[:len(data_bytes)]
    decrypted = bytes(a ^ b for a, b in zip(data_bytes, key_extended))
    return decrypted.decode('utf-8')
