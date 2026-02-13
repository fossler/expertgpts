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
        import lib.storage.streaming_cache
        monkeypatch.setattr(lib.storage.streaming_cache, 'STREAMING_CACHE_DIR', tmpdir_path)
        yield tmpdir_path


class TestStreamingCache:
    """Test suite for StreamingCache class."""

    def test_init_creates_cache_directory(self, temp_cache_dir):
        """Test that initializing StreamingCache creates cache directory."""
        from lib.storage.streaming_cache import StreamingCache

        cache = StreamingCache("test_expert")
        assert temp_cache_dir.exists()
        # Check directory has secure permissions (700)
        stat_info = os.stat(temp_cache_dir)
        permissions = oct(stat_info.st_mode)[-3:]
        assert permissions == "700"

    def test_start_streaming_to_file(self, temp_cache_dir):
        """Test starting a background streaming thread."""
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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
        from lib.storage.streaming_cache import StreamingCache

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

    def test_background_stream_continues_during_page_navigation(self, temp_cache_dir):
        """Test that streaming continues in background when user navigates away.

        This simulates the real-world scenario:
        1. User starts a chat on Expert A
        2. User navigates to Expert B while stream is still running
        3. Stream completes in background (written to cache file)
        4. User returns to Expert A
        5. Cached response is available and complete

        This is the key test for the battery-optimized background streaming feature.
        """
        from lib.storage.streaming_cache import StreamingCache

        # Setup: Create a mock client with slow streaming (simulates LLM API)
        chunks = ["This ", "is ", "a ", "long ", "response ", "from ", "the ", "AI."]
        mock_client = MockLLMClient(chunks, delay=0.05)

        # Phase 1: Start streaming on Expert A
        cache_expert_a = StreamingCache("expert_a")
        thread = cache_expert_a.start_streaming_to_file(
            client=mock_client,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        # Verify thread started
        assert thread.is_alive()

        # Phase 2: Simulate user navigating away
        # (No polling happens - user is on a different page)
        # Wait just a tiny bit to ensure thread is running
        time.sleep(0.02)

        # Verify stream is NOT complete yet (still running in background)
        assert not cache_expert_a.is_complete()

        # Phase 3: Simulate the user being on Expert B's page
        # Meanwhile, the background thread continues streaming
        # (We just wait - simulating time passing while on another page)
        time.sleep(0.6)  # Long enough for all chunks to complete

        # Phase 4: User returns to Expert A (new page load = new StreamingCache instance)
        # This simulates the template creating a new StreamingCache on page load
        cache_expert_a_returned = StreamingCache("expert_a")

        # Phase 5: Verify cached response is available
        # The response should be fully available from the cache file
        cached_response = cache_expert_a_returned.read_cache()
        assert cached_response == "This is a long response from the AI."

        # Verify stream is marked complete in metadata
        assert cache_expert_a_returned.is_complete()
        assert not cache_expert_a_returned.has_error()

        # Cleanup
        cache_expert_a_returned.cleanup()

    def test_partial_stream_resumable_after_page_navigation(self, temp_cache_dir):
        """Test that an incomplete stream can be resumed when user returns.

        This tests the scenario where user navigates away mid-stream
        and returns before the stream has completed.
        """
        from lib.storage.streaming_cache import StreamingCache

        # Setup: Create a slow streaming client
        chunks = ["First ", "Second ", "Third ", "Fourth ", "Fifth"]
        mock_client = MockLLMClient(chunks, delay=0.15)  # Slow stream

        # Phase 1: Start streaming
        cache = StreamingCache("test_expert")
        thread = cache.start_streaming_to_file(
            client=mock_client,
            messages=[],
            temperature=0.7,
            model="test-model",
            system_prompt="You are a test assistant",
            thinking_level=None
        )

        # Phase 2: Navigate away briefly (partial stream)
        time.sleep(0.2)  # Only ~1-2 chunks written

        # Phase 3: Return to page (new StreamingCache instance)
        cache_returned = StreamingCache("test_expert")

        # Verify partial content is available
        partial_response = cache_returned.read_cache()
        assert len(partial_response) > 0  # Some content was cached

        # Stream is still in progress (not complete yet)
        assert not cache_returned.is_complete()

        # Phase 4: Poll until complete (simulates poll_incomplete_stream)
        max_wait = 2.0
        start = time.time()
        while time.time() - start < max_wait:
            if cache_returned.is_complete():
                break
            time.sleep(0.1)

        # Phase 5: Verify complete response
        final_response = cache_returned.read_cache()
        assert final_response == "First Second Third Fourth Fifth"
        assert cache_returned.is_complete()

        # Cleanup
        cache_returned.cleanup()

    def test_cache_file_survives_new_instance_creation(self, temp_cache_dir):
        """Test that creating a new StreamingCache instance doesn't lose cache data.

        This verifies that the cache file is the source of truth, not the
        StreamingCache instance itself.
        """
        from lib.storage.streaming_cache import StreamingCache

        # Create initial cache and write some content
        cache1 = StreamingCache("persistent_expert")
        cache1.cache_file.write_text("Cached response content")
        cache1._write_metadata({"status": "complete", "end_time": time.time()})

        # Create a completely new instance (simulates page reload)
        cache2 = StreamingCache("persistent_expert")

        # Verify the new instance reads the same data
        assert cache2.read_cache() == "Cached response content"
        assert cache2.is_complete()

        # Cleanup
        cache2.cleanup()

    def test_background_stream_crash_resilience(self, temp_cache_dir):
        """Test that partially written cache files can be read.

        This tests the crash resilience aspect - even if only partial
        content was written, it should be readable.
        """
        from lib.storage.streaming_cache import StreamingCache

        # Simulate a partial write (e.g., app crashed mid-stream)
        cache = StreamingCache("crashed_expert")
        cache.cache_file.write_text("This is partial content")
        cache._write_metadata({"thread_id": 123, "start_time": time.time()})
        # Note: status is NOT "complete" - simulating crash

        # Create new instance (simulates app restart)
        new_cache = StreamingCache("crashed_expert")

        # Partial content should still be readable
        assert new_cache.read_cache() == "This is partial content"

        # Stream should NOT be marked complete
        assert not new_cache.is_complete()

        # Cleanup
        new_cache.cleanup()
