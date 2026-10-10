"""Tests for voice input transcription."""

import io
import wave
from types import SimpleNamespace

import pytest

from lib.audio import (
    TranscriptionResult,
    get_audio_duration,
    get_transcription_provider,
)
from lib.audio import transcription
from lib.ui.chat_toolbox import ToolboxInput


def _wav(seconds: float, rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\x00\x00" * int(seconds * rate))
    return buf.getvalue()


class _FakeTranscriptions:
    def __init__(self, text="", error=None):
        self.text, self.error, self.calls = text, error, []

    def create(self, **params):
        self.calls.append(params)
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.text)


@pytest.fixture
def fake_client(monkeypatch):
    """Replace the pooled API client; returns (fake transcriptions, used providers)."""
    fake, providers = _FakeTranscriptions(text=" Hallo Welt "), []

    def get_cached_client(provider, api_key):
        providers.append(provider)
        return SimpleNamespace(
            client=SimpleNamespace(audio=SimpleNamespace(transcriptions=fake))
        )

    monkeypatch.setattr("lib.llm.client_pool.get_cached_client", get_cached_client)
    return fake, providers


@pytest.mark.unit
class TestRouting:
    @pytest.mark.parametrize(
        "chat_provider,expected",
        [("openai", "openai"), ("deepseek", "zai"), ("zai", "zai"), ("kimi", "zai")],
    )
    def test_transcription_provider(self, chat_provider, expected):
        assert get_transcription_provider(chat_provider) == expected

    def test_models(self):
        assert transcription.TRANSCRIPTION_MODELS == {
            "openai": "gpt-transcribe",
            "zai": "glm-asr-2512",
        }
        assert transcription.MAX_DURATION_SECONDS["zai"] == 30


@pytest.mark.unit
class TestTranscribe:
    def test_openai_with_language_hint(self, fake_client):
        fake, providers = fake_client
        result = transcription.transcribe(b"wav", "openai", "key", language="zh-CN")
        assert result.success and result.text == "Hallo Welt"
        assert providers == ["openai"]
        assert fake.calls[0]["model"] == "gpt-transcribe"
        assert fake.calls[0]["language"] == "zh"
        assert fake.calls[0]["file"] == ("recording.wav", b"wav", "audio/wav")

    def test_other_providers_use_glm_asr_without_language(self, fake_client):
        fake, providers = fake_client
        transcription.transcribe(b"wav", "kimi", "key", language="de")
        assert providers == ["zai"]
        assert fake.calls[0]["model"] == "glm-asr-2512"
        assert "language" not in fake.calls[0]

    def test_api_error_becomes_error_result(self, fake_client):
        fake, _ = fake_client
        fake.error = RuntimeError("boom")
        result = transcription.transcribe(b"wav", "openai", "key")
        assert not result.success and "boom" in result.error

    def test_empty_text_is_an_error(self, fake_client):
        fake, _ = fake_client
        fake.text = "   "
        assert not transcription.transcribe(b"wav", "openai", "key").success


@pytest.mark.unit
class TestHelpers:
    def test_audio_duration(self):
        assert get_audio_duration(_wav(2.5)) == pytest.approx(2.5)
        assert get_audio_duration(b"not a wav") is None

    @pytest.mark.parametrize(
        "language,hint", [("de", "de"), ("zh-TW", "zh"), ("yue", None), (None, None)]
    )
    def test_language_hint(self, language, hint):
        assert transcription._language_hint(language) == hint

    def test_result_success(self):
        assert TranscriptionResult(text="hello").success
        assert not TranscriptionResult(error="boom").success

    def test_toolbox_input_defaults(self):
        toolbox = ToolboxInput()
        assert toolbox.attachments == [] and toolbox.images == []
        assert toolbox.voice_prompt is None
