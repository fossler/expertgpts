"""Tests for chat file and image attachments."""

import io

import pytest
from PIL import Image

from lib.shared import attachments as att
from lib.shared.attachments import (
    build_message_content,
    read_text_attachment,
    split_message_content,
    to_api_content,
    validate_image_attachment,
)
from lib.shared.constants import (
    ATTACHMENT_MAX_SIZE_KB,
    IMAGE_MAX_SIZE_MB,
    LLM_PROVIDERS,
    supports_images,
)
from lib.storage import attachment_store


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (255, 0, 0)).save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Point the attachment store at a temporary directory."""
    monkeypatch.setattr(attachment_store, "get_attachments_dir", lambda: tmp_path)
    return tmp_path


@pytest.mark.unit
class TestMessageContent:
    def test_roundtrip(self):
        attachments = [("main.py", "print('hi')\n"), ("notes.md", "# Title")]
        images = [("cat.png", "1004_x/abc.png")]
        content = build_message_content("Please review", attachments, images)
        assert split_message_content(content) == ("Please review", attachments, images)

    def test_content_contains_files_for_llm(self):
        content = build_message_content("Q", [("a.txt", "file text")])
        assert content.startswith("Q")
        assert '<attachment name="a.txt">\nfile text\n</attachment>' in content

    def test_message_without_blocks_is_unchanged(self):
        assert split_message_content("just text") == ("just text", [], [])

    def test_names_with_quotes_are_escaped(self):
        attachments = [('my "file".txt', "x")]
        content = build_message_content("Q", attachments)
        assert 'name="my &quot;file&quot;.txt"' in content
        assert split_message_content(content)[1] == attachments

    def test_marker_text_inside_prompt_is_ignored(self):
        prompt = 'Explain <image name="a" ref="b"> please'
        assert split_message_content(prompt) == (prompt, [], [])


@pytest.mark.unit
class TestValidation:
    def test_utf8_text(self):
        assert read_text_attachment("a.txt", "Grüße".encode()) == "Grüße"

    def test_text_too_large(self):
        data = b"x" * (ATTACHMENT_MAX_SIZE_KB * 1024 + 1)
        with pytest.raises(ValueError, match="too_large"):
            read_text_attachment("big.txt", data)

    def test_not_text(self):
        with pytest.raises(ValueError, match="not_text"):
            read_text_attachment("image.txt", b"\xff\xd8\xff\xe0")

    def test_valid_image(self):
        validate_image_attachment(_png_bytes())

    def test_not_an_image(self):
        with pytest.raises(ValueError, match="not_image"):
            validate_image_attachment(b"definitely not an image")

    def test_image_too_large(self):
        data = b"x" * (IMAGE_MAX_SIZE_MB * 1024 * 1024 + 1)
        with pytest.raises(ValueError, match="image_too_large"):
            validate_image_attachment(data)


@pytest.mark.unit
class TestAttachmentStore:
    def test_save_load_delete(self, store):
        ref = attachment_store.save_image("1004_x", "Cat.PNG", _png_bytes())
        assert ref.startswith("1004_x/") and ref.endswith(".png")
        assert attachment_store.get_image_path(ref).is_file()
        url = attachment_store.get_image_data_url(ref)
        assert url.startswith("data:image/png;base64,")

        attachment_store.delete_expert_attachments("1004_x")
        assert attachment_store.get_image_path(ref) is None

    def test_path_traversal_is_rejected(self, store):
        assert attachment_store.get_image_path("../../etc/passwd") is None

    def test_empty_expert_id_deletes_nothing(self, store):
        ref = attachment_store.save_image("1004_x", "a.png", _png_bytes())
        attachment_store.delete_expert_attachments("")
        assert attachment_store.get_image_path(ref) is not None


@pytest.mark.unit
class TestToApiContent:
    def test_text_only_is_unchanged(self):
        content = build_message_content("Q", [("a.txt", "x")])
        assert to_api_content(content, images_supported=True) == content

    def test_images_become_parts(self, store):
        ref = attachment_store.save_image("1004_x", "cat.png", _png_bytes())
        content = build_message_content(
            "What is this?", [("a.txt", "x")], [("cat.png", ref)]
        )
        parts = to_api_content(content, images_supported=True)
        assert parts[0]["type"] == "text"
        assert parts[0]["text"] == build_message_content(
            "What is this?", [("a.txt", "x")]
        )
        assert parts[1]["type"] == "image_url"
        assert parts[1]["image_url"]["url"].startswith("data:image/png;base64,")

    def test_images_omitted_for_text_only_models(self, store):
        ref = attachment_store.save_image("1004_x", "cat.png", _png_bytes())
        content = build_message_content("Q", [], [("cat.png", ref)])
        result = to_api_content(content, images_supported=False)
        assert result == "Q\n\n" + att._IMAGE_OMITTED.format(name="cat.png")

    def test_missing_image_becomes_note(self, store):
        content = build_message_content("Q", [], [("gone.png", "1004_x/missing.png")])
        parts = to_api_content(content, images_supported=True)
        assert parts == [
            {
                "type": "text",
                "text": "Q\n\n" + att._IMAGE_MISSING.format(name="gone.png"),
            }
        ]


@pytest.mark.unit
@pytest.mark.parametrize(
    "provider,model,expected",
    [
        ("deepseek", "deepseek-flash", True),
        ("deepseek", "deepseek-v4-pro", False),
        ("openai", "gpt-6.1-sol", True),
        ("zai", "glm-5.3", False),
        ("kimi", "kimi-k2.7-code-highspeed", True),
    ],
)
def test_supports_images(provider, model, expected):
    assert model in LLM_PROVIDERS[provider]["models"]
    assert supports_images(provider, model) is expected
