"""Tests for chat file attachments."""

import pytest

from lib.shared.attachments import (
    build_message_content,
    read_text_attachment,
    split_message_content,
)
from lib.shared.constants import ATTACHMENT_MAX_SIZE_KB


@pytest.mark.unit
class TestAttachmentContent:
    def test_roundtrip(self):
        attachments = [("main.py", "print('hi')\n"), ("notes.md", "# Title")]
        content = build_message_content("Please review", attachments)
        assert split_message_content(content) == ("Please review", attachments)

    def test_content_contains_files_for_llm(self):
        content = build_message_content("Q", [("a.txt", "file text")])
        assert content.startswith("Q")
        assert '<attachment name="a.txt">\nfile text\n</attachment>' in content

    def test_message_without_attachments_is_unchanged(self):
        assert split_message_content("just text") == ("just text", [])

    def test_names_with_quotes_are_escaped(self):
        attachments = [('my "file".txt', "x")]
        content = build_message_content("Q", attachments)
        assert 'name="my &quot;file&quot;.txt"' in content
        assert split_message_content(content)[1] == attachments


@pytest.mark.unit
class TestReadTextAttachment:
    def test_utf8_text(self):
        assert read_text_attachment("a.txt", "Grüße".encode()) == "Grüße"

    def test_too_large(self):
        data = b"x" * (ATTACHMENT_MAX_SIZE_KB * 1024 + 1)
        with pytest.raises(ValueError, match="too_large"):
            read_text_attachment("big.txt", data)

    def test_not_text(self):
        with pytest.raises(ValueError, match="not_text"):
            read_text_attachment("image.txt", b"\xff\xd8\xff\xe0")
