"""Tests for streaming cache functionality.

This test suite validates the StreamingCache class which provides
battery-optimized background streaming for LLM responses.
"""

import json
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest


class MockLLMClient:
    """Mock LLM client for testing.

    Simulates streaming by yielding chunks with a configurable delay.
    """

    def __init__(self, chunks: list, delay: float = 0.1):
        """Initialize mock client.

        Args:
            chunks: List of chunks to yield
            delay: Delay between chunks in seconds
        """
        self.chunks = chunks
        self.delay = delay

    def chat_stream(self, messages, temperature, model, system_prompt, thinking_level):
        """Simulate streaming by yielding chunks with delay."""
        for chunk in self.chunks:
            time.sleep(self.delay)
            yield chunk


@pytest.fixture
def temp_cache_dir(monkeypatch):
    """Create a temporary directory for cache files during testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        # Patch STREAMING_CACHE_DIR before importing the module
        import utils.streaming_cache
        monkeypatch.setattr(utils.streaming_cache, 'STREAMING_CACHE_DIR', tmpdir_path)
        yield tmpdir_path


class TestStreamingCache:
    """Test suite for StreamingCache class."""

    def test_init_creates_cache_directory(self, temp_cache_dir):
        """Test that initializing StreamingCache creates cache directory."""
        from utils.streaming_cache import StreamingCache

        cache = StreamingCache("test_expert")
        assert temp_cache_dir.exists()
        # Check directory has secure permissions (700)
        stat_info = os.stat(temp_cache_dir)
        permissions = oct(stat_info.st_mode)[-3:]
        assert permissions == "700"

    def test_start_streaming_to_file(self, temp_cache_dir):
        """Test starting a background streaming thread."""
        from utils.streaming_cache import StreamingCache

        mock_client = MockLLMClient(["Hello", " world", "!"], delay=0.05)
        cache = StreamingCache("test_expert")

        thread = cache.start_streaming_to_file(
            client=mock_client,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        assert thread.is_alive()
        assert isinstance(thread, threading.Thread)

        # Clean up
        cache.cleanup()

    def test_read_cache_during_streaming(self, temp_cache_dir):
        """Test reading cache while streaming is in progress."""
        from utils.streaming_cache import StreamingCache

        mock_client = MockLLMClient(["Hello", " world", "!"], delay=0.1)
        cache = StreamingCache("test_expert")

        cache.start_streaming_to_file(
            client=mock_client,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        # Wait for partial response
        time.sleep(0.15)
        partial = cache.read_cache()
        assert len(partial) > 0
        assert "Hello" in partial

        # Wait for completion
        time.sleep(0.25)
        full = cache.read_cache()
        assert full == "Hello world!"

        # Clean up
        cache.cleanup()

    def test_is_complete(self, temp_cache_dir):
        """Test completion detection."""
        from utils.streaming_cache import StreamingCache

        mock_client = MockLLMClient(["Test"], delay=0.05)
        cache = StreamingCache("test_expert")

        cache.start_streaming_to_file(
            client=mock_client,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        # Should not be complete immediately
        time.sleep(0.02)
        assert not cache.is_complete()

        # Should be complete after streaming
        time.sleep(0.2)
        assert cache.is_complete()

        # Clean up
        cache.cleanup()

    def test_cleanup_removes_cache_files(self, temp_cache_dir):
        """Test that cleanup removes cache and metadata files."""
        from utils.streaming_cache import StreamingCache

        mock_client = MockLLMClient(["Test"], delay=0.05)
        cache = StreamingCache("test_expert")

        cache.start_streaming_to_file(
            client=mock_client,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        time.sleep(0.2)  # Wait for completion

        # Verify files exist
        assert cache.cache_file.exists()
        assert cache.metadata_file.exists()

        # Cleanup
        cache.cleanup()

        # Verify files removed
        assert not cache.cache_file.exists()
        assert not cache.metadata_file.exists()

    def test_cleanup_old_cache_files(self, temp_cache_dir):
        """Test cleanup removes existing cache files before starting new stream."""
        from utils.streaming_cache import StreamingCache

        cache = StreamingCache("test_expert")

        # Create existing cache file
        existing_file = temp_cache_dir / "test_expert_latest.txt"
        existing_file.write_text("Old response")
        existing_metadata = temp_cache_dir / "test_expert_latest.meta"
        existing_metadata.write_text('{"status": "complete"}')

        # Verify files exist
        assert existing_file.exists()
        assert existing_metadata.exists()

        # Run cleanup (should remove existing files)
        cache._cleanup_old_cache_files()

        # Verify files were removed
        assert not existing_file.exists()
        assert not existing_metadata.exists()

    def test_error_handling_in_background_thread(self, temp_cache_dir):
        """Test that errors in background thread are handled correctly."""
        from utils.streaming_cache import StreamingCache

        # Create a mock client that raises an exception
        mock_client = MagicMock()
        mock_client.chat_stream.side_effect = Exception("Test API error")

        cache = StreamingCache("test_expert")

        cache.start_streaming_to_file(
            client=mock_client,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        # Wait for thread to complete
        time.sleep(0.2)

        # Check that error was detected
        assert cache.has_error()
        error_msg = cache.get_error()
        assert "Test API error" in error_msg

        # Clean up
        cache.cleanup()

    def test_metadata_tracking(self, temp_cache_dir):
        """Test that metadata is correctly written and read."""
        from utils.streaming_cache import StreamingCache

        cache = StreamingCache("test_expert")

        # Write metadata
        cache._write_metadata({"status": "test_status", "test_key": "test_value"})

        # Read metadata
        metadata = cache._read_metadata()

        assert metadata.get("status") == "test_status"
        assert metadata.get("test_key") == "test_value"

        # Clean up
        cache.cleanup()

    def test_multiple_cache_files_coexist(self, temp_cache_dir):
        """Test that multiple cache files can coexist for different experts."""
        from utils.streaming_cache import StreamingCache

        cache1 = StreamingCache("expert_1")
        cache2 = StreamingCache("expert_2")

        # Create cache files for both experts
        cache1.cache_file.write_text("Response 1")
        cache2.cache_file.write_text("Response 2")

        # Verify both exist
        assert cache1.cache_file.exists()
        assert cache2.cache_file.exists()

        # Verify they have different paths
        assert cache1.cache_file != cache2.cache_file

        # Clean up
        cache1.cleanup()
        cache2.cleanup()

    def test_concurrent_streaming_different_experts(self, temp_cache_dir):
        """Test that concurrent streaming for different experts works correctly."""
        from utils.streaming_cache import StreamingCache

        # Create two caches for different experts
        cache1 = StreamingCache("expert_1")
        cache2 = StreamingCache("expert_2")

        # Start streaming for both
        mock_client1 = MockLLMClient(["Expert 1 response"], delay=0.05)
        mock_client2 = MockLLMClient(["Expert 2 response"], delay=0.05)

        thread1 = cache1.start_streaming_to_file(
            client=mock_client1,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are expert 1",
            thinking_level=None
        )

        thread2 = cache2.start_streaming_to_file(
            client=mock_client2,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are expert 2",
            thinking_level=None
        )

        # Both threads should be alive
        assert thread1.is_alive()
        assert thread2.is_alive()

        # Wait for completion
        time.sleep(0.3)

        # Verify both responses are correct
        response1 = cache1.read_cache()
        response2 = cache2.read_cache()

        assert response1 == "Expert 1 response"
        assert response2 == "Expert 2 response"

        # Clean up
        cache1.cleanup()
        cache2.cleanup()
