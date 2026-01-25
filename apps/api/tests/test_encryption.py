"""
Unit tests for encryption service.
"""

import pytest

from encryption import EncryptionService


class TestEncryptionService:
    """Test cases for encryption/decryption functionality."""

    def test_encrypt_decrypt_simple_text(self):
        """Test basic encryption and decryption of simple text."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "Hello, World!"

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_decrypt_api_key(self):
        """Test encryption and decryption of API key."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "sk-1234567890abcdefghijklmnop"

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_decrypt_special_characters(self):
        """Test encryption and decryption with special characters."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "Test@#$%^&*()_+-=[]{}|;:',.<>?/~`"

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_decrypt_unicode(self):
        """Test encryption and decryption with unicode characters."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "你好世界 🌍 Ñoño café"

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encryption_format(self):
        """Test that encrypted string follows expected format."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "test"

        encrypted = encryption_service.encrypt(plaintext)

        # Format should be: iv:auth_tag:encrypted_content
        parts = encrypted.split(":")
        assert len(parts) == 3

        iv_hex, auth_tag_hex, encrypted_hex = parts

        # IV should be 12 bytes = 24 hex chars
        assert len(iv_hex) == 24

        # Auth tag should be 16 bytes = 32 hex chars
        assert len(auth_tag_hex) == 32

        # Encrypted content should be at least some length
        assert len(encrypted_hex) > 0

    def test_encryption_uniqueness(self):
        """Test that encrypting the same text twice produces different ciphertexts."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "same text"

        encrypted1 = encryption_service.encrypt(plaintext)
        encrypted2 = encryption_service.encrypt(plaintext)

        # Should be different due to random IV
        assert encrypted1 != encrypted2

        # But both should decrypt to the same plaintext
        assert encryption_service.decrypt(encrypted1) == plaintext
        assert encryption_service.decrypt(encrypted2) == plaintext

    def test_invalid_key_length_raises_error(self):
        """Test that invalid key length raises ValueError."""
        with pytest.raises(ValueError, match="must be 32 bytes"):
            EncryptionService("0123456789abcdef")  # Only 16 bytes

    def test_invalid_encrypted_format_raises_error(self):
        """Test that invalid encrypted format raises ValueError."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )

        with pytest.raises(ValueError, match="Invalid encrypted format"):
            encryption_service.decrypt("invalid_format")

    def test_tampered_encrypted_data_raises_error(self):
        """Test that tampered encrypted data raises decryption error."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "secret"

        encrypted = encryption_service.encrypt(plaintext)

        # Tamper with the encrypted data
        tampered = encrypted[:-1] + "0"  # Change last character

        with pytest.raises(ValueError, match="Decryption failed"):
            encryption_service.decrypt(tampered)

    def test_empty_string(self):
        """Test encryption and decryption of empty string."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = ""

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_long_text(self):
        """Test encryption and decryption of long text."""
        encryption_service = EncryptionService(
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        )
        plaintext = "A" * 10000  # 10KB of text

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_singleton_instance(self):
        """Test that singleton instance works correctly."""
        from encryption import encryption_service

        plaintext = "test singleton"

        encrypted = encryption_service.encrypt(plaintext)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == plaintext
