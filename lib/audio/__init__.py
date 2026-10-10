"""Audio processing (voice input)."""

from lib.audio.transcription import (
    TranscriptionResult,
    is_transcription_available,
    transcribe,
)

__all__ = [
    "TranscriptionResult",
    "is_transcription_available",
    "transcribe",
]
