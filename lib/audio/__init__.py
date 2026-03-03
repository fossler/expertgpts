"""Audio processing utilities for ExpertGPTs."""

from lib.audio.transcription_client import (
    TranscriptionClient,
    TranscriptionResult,
    estimate_audio_duration,
    MAX_AUDIO_DURATION_SECONDS,
    MAX_FILE_SIZE_BYTES,
)

__all__ = [
    "TranscriptionClient",
    "TranscriptionResult",
    "estimate_audio_duration",
    "MAX_AUDIO_DURATION_SECONDS",
    "MAX_FILE_SIZE_BYTES",
]
