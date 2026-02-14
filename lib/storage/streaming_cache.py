"""Streaming cache manager for background LLM responses.

This module provides file-based caching for streaming LLM responses,
allowing responses to complete in the background when users navigate
away from the expert page.

Key benefits:
- Battery optimized: File I/O uses DMA, CPU can deep sleep between reads
- Crash resilient: Cache files survive app restarts
- Easy debugging: Inspect .txt cache files manually
- Thread-safe: OS-level file locking prevents corruption
"""

import os
import threading
import time
from pathlib import Path
from typing import Optional

from lib.llm.llm_client import LLMClient
from lib.shared.format_ops import read_json, write_json
from lib.shared.file_ops import ensure_directory_exists, set_secure_permissions

STREAMING_CACHE_DIR = Path("streaming_cache")


class StreamingCache:
    """Manages file-based caching for streaming LLM responses.

    This class handles background streaming by writing chunks to cache files,
    allowing responses to complete even when users navigate away.
    """

    def __init__(self, expert_id: str):
        """Initialize streaming cache for an expert.

        Args:
            expert_id: Expert identifier (e.g., "1001_python_expert")
        """
        self.expert_id = expert_id

        # Use a fixed filename (not timestamp-based) so all StreamingCache
        # instances for the same expert reference the same files
        self.cache_file = STREAMING_CACHE_DIR / f"{expert_id}_latest.txt"
        self.metadata_file = STREAMING_CACHE_DIR / f"{expert_id}_latest.meta"

        # Ensure cache directory exists with secure permissions
        ensure_directory_exists(STREAMING_CACHE_DIR, permissions=0o700)

    def start_streaming_to_file(
        self,
        client: LLMClient,
        messages: list[dict],
        temperature: float,
        model: str,
        system_prompt: str,
        thinking_level: Optional[str]
    ) -> threading.Thread:
        """Start a background thread that streams LLM response to file.

        Args:
            client: LLM client instance
            messages: Messages to send to LLM
            temperature: Temperature for generation
            model: Model name
            system_prompt: System prompt to use
            thinking_level: Thinking level (for reasoning models)

        Returns:
            Thread object for the background streamer
        """
        # Clear previous cache files for this expert
        self._cleanup_old_cache_files()

        # Create and start daemon thread
        thread = threading.Thread(
            target=self._stream_to_file,
            args=(client, messages, temperature, model,
                  system_prompt, thinking_level),
            daemon=True
        )
        thread.start()

        # Store thread info in metadata
        self._write_metadata({"thread_id": thread.ident, "start_time": time.time()})

        return thread

    def _stream_to_file(
        self,
        client: LLMClient,
        messages: list[dict],
        temperature: float,
        model: str,
        system_prompt: str,
        thinking_level: Optional[str]
    ) -> None:
        """Execute API call in background thread and write chunks to file.

        This method runs in a daemon thread and writes each chunk to the
        cache file as it arrives from the LLM API.

        Note: Uses fsync() for crash resilience - data is forced to disk
        immediately after each chunk is written.
        """
        try:
            # Create file with secure permissions if it doesn't exist
            if not self.cache_file.exists():
                self.cache_file.touch()
                set_secure_permissions(self.cache_file)

            with open(self.cache_file, 'a', encoding='utf-8') as f:
                for chunk in client.chat_stream(
                    messages=messages,
                    temperature=temperature,
                    model=model,
                    system_prompt=system_prompt,
                    thinking_level=thinking_level
                ):
                    f.write(chunk)
                    f.flush()  # Ensure immediate write to disk
                    os.fsync(f.fileno())  # Force write to disk (crash resilient)

            # Mark completion in metadata
            self._write_metadata({"status": "complete", "end_time": time.time()})

        except Exception as e:
            # Create file with secure permissions if it doesn't exist
            if not self.cache_file.exists():
                self.cache_file.touch()
                set_secure_permissions(self.cache_file)

            # Write error to file for debugging
            with open(self.cache_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[STREAMING ERROR: {str(e)}]")

            # Mark error in metadata
            self._write_metadata({"status": "error", "error": str(e)})

    def read_cache(self) -> str:
        """Read current cache contents.

        Returns:
            Current response text (empty if cache doesn't exist)
        """
        try:
            if self.cache_file.exists():
                return self.cache_file.read_text(encoding='utf-8')
        except Exception:
            pass
        return ""

    def is_complete(self) -> bool:
        """Check if streaming is complete.

        Returns:
            True if streaming is marked complete in metadata
        """
        try:
            metadata = self._read_metadata()
            return metadata.get("status") == "complete"
        except Exception:
            return False

    def has_error(self) -> bool:
        """Check if streaming encountered an error.

        Returns:
            True if error occurred during streaming
        """
        try:
            metadata = self._read_metadata()
            return metadata.get("status") == "error"
        except Exception:
            return False

    def get_error(self) -> Optional[str]:
        """Get error message if streaming failed.

        Returns:
            Error message or None
        """
        try:
            metadata = self._read_metadata()
            return metadata.get("error")
        except Exception:
            return None

    def cleanup(self) -> None:
        """Remove cache files after saving to chat history.

        Should be called after response is saved to chat_history.
        Uses best-effort cleanup - errors are silently ignored.
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
        except Exception:
            pass  # Best-effort cleanup

    def _cleanup_old_cache_files(self) -> None:
        """Remove existing cache files for this expert before starting new stream.

        Only removes files if they are from a PREVIOUS completed stream,
        not if they're currently being written to.

        This ensures we don't delete files that are actively being used
        by a background thread from a previous page load.
        """
        try:
            # Check if metadata exists and indicates completion
            if self.metadata_file.exists():
                metadata = self._read_metadata()

                # Only delete if marked as complete (finished stream)
                # or if it has an error (failed stream)
                # Don't delete if streaming is in progress
                if metadata.get("status") in ["complete", "error"]:
                    if self.cache_file.exists():
                        self.cache_file.unlink()
                    self.metadata_file.unlink()
            else:
                # No metadata exists, safe to delete cache file (orphaned)
                if self.cache_file.exists():
                    self.cache_file.unlink()
        except Exception:
            pass  # Best-effort cleanup

    def _write_metadata(self, data: dict) -> None:
        """Write metadata to metadata file.

        Args:
            data: Dictionary of metadata to write (merged with existing)
        """
        try:
            # Read existing metadata and update it
            existing_metadata = self._read_metadata()
            existing_metadata.update(data)

            write_json(self.metadata_file, existing_metadata)
        except Exception:
            pass

    def _read_metadata(self) -> dict:
        """Read metadata from metadata file.

        Returns:
            Dictionary of metadata (empty if file doesn't exist)
        """
        try:
            if self.metadata_file.exists():
                metadata = read_json(self.metadata_file)
                return metadata if metadata is not None else {}
        except Exception:
            pass
        return {}
