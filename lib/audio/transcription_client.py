"""Z.AI GLM-ASR transcription client.

This module provides a client for transcribing audio using Z.AI's
GLM-ASR-2512 Automatic Speech Recognition model.
"""

import requests
from typing import Optional
from dataclasses import dataclass
from io import BytesIO

from lib.shared.constants import get_provider_base_url
from lib.shared.helpers import sanitize_error_message


# Z.AI ASR Configuration
ZAI_ASR_MODEL = "glm-asr-2512"
ZAI_ASR_ENDPOINT = "/audio/transcriptions"
MAX_AUDIO_DURATION_SECONDS = 30
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


@dataclass
class TranscriptionResult:
    """Result of an audio transcription.

    Attributes:
        text: The transcribed text (empty if failed)
        duration_seconds: Optional audio duration in seconds
        success: Whether transcription was successful
        error: Error message if transcription failed
    """
    text: str
    duration_seconds: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class TranscriptionClient:
    """Client for Z.AI's GLM-ASR speech recognition API.

    Uses direct HTTP requests to Z.AI's transcription endpoint
    for maximum compatibility and control.

    Example:
        >>> client = TranscriptionClient(api_key="your-zai-api-key")
        >>> audio_data = BytesIO(wav_bytes)
        >>> result = client.transcribe(audio_data)
        >>> if result.success:
        ...     print(result.text)
    """

    def __init__(self, api_key: str):
        """Initialize the transcription client.

        Args:
            api_key: Z.AI API key

        Raises:
            ValueError: If API key is empty
        """
        if not api_key:
            raise ValueError("Z.AI API key must be provided")

        self.api_key = api_key
        # Z.AI base URL: https://api.z.ai/api/paas/v4
        self.base_url = get_provider_base_url("zai")

    def transcribe(
        self,
        audio_data: BytesIO,
        filename: str = "audio.wav"
    ) -> TranscriptionResult:
        """Transcribe audio using Z.AI's GLM-ASR model.

        Args:
            audio_data: Audio data as a file-like object (BytesIO)
            filename: Filename for the audio (used for MIME type detection)

        Returns:
            TranscriptionResult with transcription text or error
        """
        # Validate file size
        audio_data.seek(0, 2)  # Seek to end
        file_size = audio_data.tell()
        audio_data.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE_BYTES:
            return TranscriptionResult(
                text="",
                success=False,
                error=f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds maximum (25 MB)"
            )

        # Construct API URL
        url = f"{self.base_url}{ZAI_ASR_ENDPOINT}"

        # Prepare multipart form data
        files = {
            "file": (filename, audio_data, "audio/wav")
        }
        data = {
            "model": ZAI_ASR_MODEL,
            "stream": "false"  # Non-streaming for simplicity
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                headers=headers,
                timeout=60  # 60 second timeout
            )

            if response.status_code == 200:
                result = response.json()
                # Z.AI returns {"text": "transcribed text"}
                transcription_text = result.get("text", "")
                return TranscriptionResult(
                    text=transcription_text,
                    success=True
                )
            else:
                error_msg = self._parse_error_response(response)
                return TranscriptionResult(
                    text="",
                    success=False,
                    error=error_msg
                )

        except requests.exceptions.Timeout:
            return TranscriptionResult(
                text="",
                success=False,
                error="Request timed out. Please try again."
            )
        except requests.exceptions.ConnectionError:
            return TranscriptionResult(
                text="",
                success=False,
                error="Could not connect to Z.AI servers. Check your connection."
            )
        except Exception as e:
            return TranscriptionResult(
                text="",
                success=False,
                error=sanitize_error_message(str(e))
            )

    def _parse_error_response(self, response) -> str:
        """Parse error response from API.

        Args:
            response: requests Response object

        Returns:
            User-friendly error message
        """
        try:
            error_data = response.json()
            if "error" in error_data:
                error_obj = error_data["error"]
                if isinstance(error_obj, dict):
                    return sanitize_error_message(error_obj.get("message", "Unknown error"))
                return sanitize_error_message(str(error_obj))
            if "message" in error_data:
                return sanitize_error_message(error_data["message"])
        except Exception:
            pass

        return f"API error (status {response.status_code})"


def estimate_audio_duration(audio_data: BytesIO, sample_rate: int = 16000) -> float:
    """Estimate audio duration from WAV data.

    Simple estimation based on file size for 16-bit mono WAV.
    This is an approximation - actual duration may vary.

    Args:
        audio_data: Audio data as BytesIO
        sample_rate: Sample rate (default 16000 Hz for st.audio_input)

    Returns:
        Estimated duration in seconds
    """
    audio_data.seek(0, 2)
    file_size = audio_data.tell()
    audio_data.seek(0)

    # WAV header is typically 44 bytes
    # 16-bit mono = 2 bytes per sample
    data_size = max(0, file_size - 44)
    bytes_per_second = sample_rate * 2

    return data_size / bytes_per_second if bytes_per_second > 0 else 0
