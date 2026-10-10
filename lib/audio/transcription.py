"""Speech-to-text for voice input in the chat toolbox.

Scaffold: the toolbox records audio and calls ``transcribe()``, but no
speech-to-text model is connected yet, so ``is_transcription_available()``
returns False and the toolbox only shows a notice.

To connect a model, implement ``transcribe()`` (e.g. OpenAI
``/audio/transcriptions`` or Z.AI GLM-ASR, see the unmerged
``feature/voiceTranscription`` branch) and make
``is_transcription_available()`` return True when it can be used.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptionResult:
    """Result of a transcription.

    Attributes:
        text: Transcribed text (empty on failure)
        error: Error message if the transcription failed
    """

    text: str = ""
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether the transcription produced text without an error."""
        return self.error is None


def is_transcription_available() -> bool:
    """Whether a speech-to-text model is connected.

    Returns:
        bool: False until ``transcribe()`` is implemented
    """
    return False


def transcribe(
    audio: bytes, mime_type: str = "audio/wav", language: Optional[str] = None
) -> TranscriptionResult:
    """Transcribe recorded audio to text.

    Args:
        audio: Recorded audio bytes (WAV from ``st.audio_input``)
        mime_type: MIME type of the audio
        language: Optional language code hint (e.g. "de")

    Returns:
        TranscriptionResult: Always an error result until a model is connected
    """
    return TranscriptionResult(error="Speech-to-text is not connected yet")
