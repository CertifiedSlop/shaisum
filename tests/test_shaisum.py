"""
Tests for shAIsum - SHA256-like Hash Function Powered by LLM

Note: These tests verify the API works correctly. They do not verify
cryptographic properties because shAIsum operates on vibes, not math.
"""

import tempfile
import pytest
from shaisum import SHAIsum, shaisum


class TestSHAIsumHashing:
    """Test hashing functionality."""

    def test_hash_returns_64_char_hex(self):
        """Test that hash returns 64-character hex string."""
        hasher = SHAIsum()
        h = hasher.hash("test data")
        
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h.lower())

    def test_hash_caching(self):
        """Test that hash results are cached."""
        hasher = SHAIsum()
        h1 = hasher.hash("test data")
        h2 = hasher.hash("test data")
        
        # Should return the same hash from cache
        assert h1 == h2

    def test_hash_different_inputs(self):
        """Test that different inputs produce hashes."""
        hasher = SHAIsum()
        h1 = hasher.hash("input one")
        h2 = hasher.hash("input two")
        
        # Both should be valid 64-char hex
        assert len(h1) == 64
        assert len(h2) == 64

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        hasher = SHAIsum()
        h = hasher.hash("")
        
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h.lower())

    def test_clear_cache(self):
        """Test clearing the cache."""
        hasher = SHAIsum()
        hasher.hash("test data")
        
        hasher.clear_cache()
        
        # Cache should be empty after clear
        assert len(hasher._cache) == 0


class TestSHAIsumFileHashing:
    """Test file hashing functionality."""

    def test_hash_text_file(self, tmp_path):
        """Test hashing a text file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        
        hasher = SHAIsum()
        h = hasher.hash_file(str(test_file))
        
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h.lower())

    def test_hash_binary_file(self, tmp_path):
        """Test hashing a binary file."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b'\x00\x01\x02\x03')
        
        hasher = SHAIsum()
        h = hasher.hash_file(str(test_file))
        
        assert len(h) == 64

    def test_hash_nonexistent_file(self):
        """Test hashing a nonexistent file returns fallback."""
        hasher = SHAIsum()
        h = hasher.hash_file("/nonexistent/path/file.txt")
        
        # Should return fallback hash
        assert len(h) == 64


class TestSHAIsumVerification:
    """Test hash verification functionality."""

    def test_verify_matching_hash(self):
        """Test verifying a matching hash."""
        hasher = SHAIsum()
        h = hasher.hash("test data")
        
        assert hasher.verify("test data", h) is True

    def test_verify_non_matching_hash(self):
        """Test verifying a non-matching hash."""
        hasher = SHAIsum()
        h = hasher.hash("test data")
        
        # Different input should not match
        assert hasher.verify("different data", h) is False

        def test_verify_case_insensitive(self):
        """Test that verification is case-insensitive."""
        hasher = SHAIsum()
        h = hasher.hash("test data")
        
        # Both upper and lower case should work
        assert hasher.verify("test data", h.upper()) is True
        assert hasher.verify("test data", h.lower()) is True


class TestSHAIsumBackend:
    """Test backend configuration."""

    def test_default_backend_is_ollama(self):
        """Test that Ollama is the default backend."""
        hasher = SHAIsum()
        assert hasher._backend.__class__.__name__ == "_OllamaBackend"

    def test_unknown_backend_raises(self):
        """Test that unknown backend raises ValueError."""
        with pytest.raises(ValueError, match="Unknown backend"):
            SHAIsum(backend="nonexistent")

    def test_backend_custom_model(self):
        """Test setting a custom model."""
        hasher = SHAIsum(model="llama3.1")
        assert hasher._backend.model == "llama3.1"


class TestShaisumConvenienceFunction:
    """Test the convenience function."""

    def test_shaisum_returns_64_char_hex(self):
        """Test that shaisum returns 64-char hex."""
        h = shaisum("test data")
        
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h.lower())

    def test_shaisum_with_backend(self):
        """Test shaisum with specific backend."""
        h = shaisum("test data", backend="ollama")
        
        assert len(h) == 64

    def test_shaisum_with_model(self):
        """Test shaisum with specific model."""
        h = shaisum("test data", backend="ollama", model="llama3.2")
        
        assert len(h) == 64


class TestFallbackHash:
    """Test fallback hash generation."""

    def test_fallback_produces_64_chars(self):
        """Test that fallback produces 64-char hex."""
        hasher = SHAIsum()
        h = hasher._fallback("test data")
        
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h)

    def test_fallback_deterministic(self):
        """Test that fallback is deterministic for same input."""
        hasher = SHAIsum()
        h1 = hasher._fallback("test data")
        h2 = hasher._fallback("test data")
        
        assert h1 == h2

    def test_fallback_different_inputs(self):
        """Test that fallback produces different hashes for different inputs."""
        hasher = SHAIsum()
        h1 = hasher._fallback("input one")
        h2 = hasher._fallback("input two")
        
        # Different inputs should produce different fallback hashes
        assert h1 != h2


class TestHashValidation:
    """Test hash validation."""

    def test_validate_valid_hash(self):
        """Test validating a valid 64-char hex hash."""
        hasher = SHAIsum()
        valid_hash = "a" * 64
        
        assert hasher._validate(valid_hash) is True

    def test_validate_invalid_hash_wrong_length(self):
        """Test validating hash with wrong length."""
        hasher = SHAIsum()
        invalid_hash = "a" * 32
        
        assert hasher._validate(invalid_hash) is False

    def test_validate_invalid_hash_non_hex(self):
        """Test validating hash with non-hex characters."""
        hasher = SHAIsum()
        invalid_hash = "g" * 64  # 'g' is not hex
        
        assert hasher._validate(invalid_hash) is False
