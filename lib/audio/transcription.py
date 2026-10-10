"""Speech-to-text for voice input in the chat toolbox.

Experts that chat with OpenAI transcribe with OpenAI's transcription model;
all other experts (DeepSeek, Z.AI, KIMI) use Z.AI's GLM-ASR. Both providers
expose an OpenAI-compatible ``/audio/transcriptions`` endpoint, so the pooled
OpenAI-compatible client is used for both.
"""

import io
import wave
from dataclasses import dataclass
from typing import Optional

from lib.shared.helpers import sanitize_error_message

# Transcription model per transcription provider
TRANSCRIPTION_MODELS = {
    "openai": "gpt-transcribe",
    "zai": "glm-asr-2512",
}

# Maximum recording length per transcription provider (None = no limit)
MAX_DURATION_SECONDS = {
    "openai": None,
    "zai": 30,
}


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


def get_transcription_provider(chat_provider: str) -> str:
    """Get the provider used to transcribe voice input for an expert.

    Args:
        chat_provider: The expert's chat provider (e.g. "openai", "deepseek")

    Returns:
        str: "openai" for OpenAI experts, otherwise "zai"
    """
    return "openai" if chat_provider == "openai" else "zai"


def get_audio_duration(audio: bytes) -> Optional[float]:
    """Get the duration of a WAV recording.

    Args:
        audio: WAV bytes (as recorded by ``st.audio_input``)

    Returns:
        float | None: Duration in seconds, or None if the audio isn't WAV
    """
    try:
        with wave.open(io.BytesIO(audio)) as wav:
            return wav.getnframes() / float(wav.getframerate())
    except (wave.Error, EOFError, ZeroDivisionError):
        return None


def _language_hint(language: Optional[str]) -> Optional[str]:
    """Map an app language code to an ISO-639-1 hint (e.g. "zh-CN" -> "zh")."""
    if not language:
        return None
    code = language.split("-")[0].lower()
    return code if len(code) == 2 else None


def transcribe(
    audio: bytes,
    chat_provider: str,
    api_key: str,
    mime_type: str = "audio/wav",
    language: Optional[str] = None,
) -> TranscriptionResult:
    """Transcribe recorded audio to text.

    Args:
        audio: Recorded audio bytes (WAV from ``st.audio_input``)
        chat_provider: The expert's chat provider; selects the transcription
            provider via ``get_transcription_provider()``
        api_key: API key of the transcription provider
        mime_type: MIME type of the audio
        language: Optional app language code used as a hint (OpenAI only)

    Returns:
        TranscriptionResult: The text, or an error message
    """
    from lib.llm.client_pool import get_cached_client

    provider = get_transcription_provider(chat_provider)
    params = {
        "model": TRANSCRIPTION_MODELS[provider],
        "file": ("recording.wav", audio, mime_type),
    }
    hint = _language_hint(language)
    if provider == "openai" and hint:
        params["language"] = hint

    try:
        client = get_cached_client(provider=provider, api_key=api_key).client
        response = client.audio.transcriptions.create(**params)
    except Exception as e:
        return TranscriptionResult(error=sanitize_error_message(str(e)))

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        return TranscriptionResult(error="No speech recognized")
    return TranscriptionResult(text=text)
