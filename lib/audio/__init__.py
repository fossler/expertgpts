"""Audio processing (voice input)."""

from lib.audio.transcription import (
    MAX_DURATION_SECONDS,
    TRANSCRIPTION_MODELS,
    TranscriptionResult,
    get_audio_duration,
    get_transcription_provider,
    transcribe,
)

__all__ = [
    "MAX_DURATION_SECONDS",
    "TRANSCRIPTION_MODELS",
    "TranscriptionResult",
    "get_audio_duration",
    "get_transcription_provider",
    "transcribe",
]
