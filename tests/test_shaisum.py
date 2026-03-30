"""
Tests for shAIsum - SHA256-like Hash Function Powered by LLM

Note: These tests verify the API works correctly. They do not verify
cryptographic properties because shAIsum is not a cryptographic hash function.
"""

import tempfile
import pytest
from aiuth import SHAIsum, shaisum


class TestSHAIsumBasic:
    """Test basic hash functionality."""

    def test_hash_returns_string(self):
        """Test that hash returns a string."""
        hasher = SHAIsum()
        result = hasher.hash("test input")
        assert isinstance(result, str)

    def test_hash_returns_64_chars(self):
        """Test that hash returns exactly 64 characters."""
        hasher = SHAIsum()
        result = hasher.hash("test input")
        assert len(result) == 64

    def test_hash_is_hexadecimal(self):
        """Test that hash contains only hexadecimal characters."""
        hasher = SHAIsum()
        result = hasher.hash("test input")
        assert all(c in '0123456789abcdef' for c in result.lower())

    def test_hash_deterministic_in_session(self):
        """Test that same input produces same hash in same session (cached)."""
        hasher = SHAIsum()
        h1 = hasher.hash("test input")
        h2 = hasher.hash("test input")
        assert h1 == h2

    def test_different_inputs_different_hashes(self):
        """Test that different inputs produce different hashes."""
        hasher = SHAIsum()
        h1 = hasher.hash("input one")
        h2 = hasher.hash("input two")
        assert h1 != h2

        def test_empty_input(self):
        """Test hashing empty input."""
        hasher = SHAIsum()
        result = hasher.hash("")
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result.lower())


class TestSHAIsumCache:
    """Test cache functionality."""

    def test_clear_cache(self):
        """Test that clear_cache works."""
        hasher = SHAIsum()
        h1 = hasher.hash("test")
        hasher.clear_cache()
        h2 = hasher.hash("test")
        assert len(h2) == 64

    def test_cache_returns_same_value(self):
        """Test that cached values are returned correctly."""
        hasher = SHAIsum()
        h1 = hasher.hash("cached test")
        h2 = hasher.hash("cached test")
        assert h1 == h2


class TestSHAIsumVerify:
    """Test hash verification."""

    def test_verify_matching_hash(self):
        """Test verification with matching hash."""
        hasher = SHAIsum()
        h = hasher.hash("test data")
        assert hasher.verify("test data", h) is True

    def test_verify_non_matching_hash(self):
        """Test verification with non-matching hash."""
        hasher = SHAIsum()
        fake_hash = "a" * 64
        assert hasher.verify("test data", fake_hash) is False

    def test_verify_case_insensitive(self):
        """Test that verification is case-insensitive."""
        hasher = SHAIsum()
        h = hasher.hash("test data")
        assert hasher.verify("test data", h.upper()) is True


class TestSHAIsumFile:
    """Test file hashing."""

    def test_hash_file(self, tmp_path):
        """Test hashing a file."""
        hasher = SHAIsum()
        test_file = tmp_path / "test.txt"
        test_file.write_text("file content")
        result = hasher.hash_file(str(test_file))
        assert len(result) == 64

    def test_hash_file_not_found(self):
        """Test hashing a non-existent file."""
        hasher = SHAIsum()
        result = hasher.hash_file("/nonexistent/path/file.txt")
        assert len(result) == 64


class TestConvenienceFunction:
    """Test the shaisum convenience function."""

    def test_shaisum_returns_string(self):
        """Test that shaisum returns a string."""
        result = shaisum("test input")
        assert isinstance(result, str)

    def test_shaisum_returns_64_chars(self):
        """Test that shaisum returns 64 characters."""
        result = shaisum("test input")
        assert len(result) == 64


class TestSHAIsumFallback:
    """Test fallback hash generation."""

        def test_fallback_hash_length(self):
        """Test that fallback hash is 64 characters."""
        hasher = SHAIsum()
        result = hasher._fallback("test")
        assert len(result) == 64

    def test_fallback_hash_deterministic(self):
        """Test that fallback hash is deterministic."""
        hasher = SHAIsum()
        h1 = hasher._fallback("test")
        h2 = hasher._fallback("test")
        assert h1 == h2
