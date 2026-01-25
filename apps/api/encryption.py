"""
Encryption Service for Credential Vault.

Uses AES-256-GCM encryption via the cryptography library.
"""

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

from settings import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive credential data."""

    def __init__(self, encryption_key: str | None = None):
        """
        Initialize encryption service.

        Args:
            encryption_key: 64-character hex string (32 bytes). If None, reads from settings.
        """
        if encryption_key is None:
            encryption_key = settings.encryption_key

        # Convert hex string to bytes
        self.key = bytes.fromhex(encryption_key)

        # Validate key length (must be 32 bytes for AES-256)
        if len(self.key) != 32:
            raise ValueError(
                f"Encryption key must be 32 bytes (64 hex chars), got {len(self.key)} bytes"
            )

        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: Text to encrypt

        Returns:
            Encrypted string in format: iv:auth_tag:encrypted_content
            (all hex-encoded)
        """
        # Generate a random 12-byte IV (nonce) for GCM
        iv = os.urandom(12)

        # Encrypt the plaintext (must be bytes)
        plaintext_bytes = plaintext.encode("utf-8")
        ciphertext = self.aesgcm.encrypt(iv, plaintext_bytes, None)

        # Split into ciphertext (first part) and auth tag (last 16 bytes)
        # GCM appends the auth tag to the ciphertext
        auth_tag = ciphertext[-16:]
        encrypted_content = ciphertext[:-16]

        # Encode to hex and combine with colons
        iv_hex = iv.hex()
        auth_tag_hex = auth_tag.hex()
        encrypted_hex = encrypted_content.hex()

        return f"{iv_hex}:{auth_tag_hex}:{encrypted_hex}"

    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt ciphertext using AES-256-GCM.

        Args:
            encrypted_text: Encrypted string in format: iv:auth_tag:encrypted_content

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If format is invalid or decryption fails
        """
        try:
            # Parse the encrypted string
            parts = encrypted_text.split(":")
            if len(parts) != 3:
                raise ValueError(
                    "Invalid encrypted format. Expected: iv:auth_tag:encrypted_content"
                )

            iv_hex, auth_tag_hex, encrypted_hex = parts

            # Decode from hex
            iv = bytes.fromhex(iv_hex)
            auth_tag = bytes.fromhex(auth_tag_hex)
            encrypted_content = bytes.fromhex(encrypted_hex)

            # Reconstruct the ciphertext with auth tag
            ciphertext = encrypted_content + auth_tag

            # Decrypt
            plaintext_bytes = self.aesgcm.decrypt(iv, ciphertext, None)

            return plaintext_bytes.decode("utf-8")

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}") from e


# Singleton instance
encryption_service = EncryptionService()
