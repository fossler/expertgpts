"""Tests for the voice input scaffold."""

import pytest

from lib.audio import TranscriptionResult, is_transcription_available, transcribe
from lib.ui.chat_toolbox import ToolboxInput


@pytest.mark.unit
class TestTranscriptionScaffold:
    def test_not_available_yet(self):
        assert is_transcription_available() is False

    def test_transcribe_returns_error_result(self):
        result = transcribe(b"RIFF....WAVE")
        assert not result.success
        assert result.text == ""

    def test_result_success(self):
        assert TranscriptionResult(text="hello").success
        assert not TranscriptionResult(error="boom").success


@pytest.mark.unit
def test_toolbox_input_defaults():
    toolbox = ToolboxInput()
    assert toolbox.attachments == [] and toolbox.images == []
    assert toolbox.voice_prompt is None
