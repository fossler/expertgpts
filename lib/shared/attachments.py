"""File and image attachments for chat messages.

Attachments are embedded into the user message content, so token counting,
chat history persistence and size limits work unchanged:

- Text files are wrapped in ``<attachment name="...">...</attachment>`` blocks.
- Images are stored on disk (``lib.storage.attachment_store``) and referenced
  by an ``<image name="..." ref="...">`` tag. ``to_api_content()`` turns these
  into image parts when a request is sent to the LLM.

All blocks follow the prompt; ``split_message_content()`` reverses this for
display.
"""

import html
import io
import re
from typing import List, Tuple, Union

from PIL import Image as PILImage

from lib.shared.constants import ATTACHMENT_MAX_SIZE_KB, IMAGE_MAX_SIZE_MB

# (file name, file text)
Attachment = Tuple[str, str]
# (file name, stored image reference)
ImageRef = Tuple[str, str]

_BLOCK_RE = re.compile(
    r'\n\n(?:<image name="(?P<image_name>[^"]*)" ref="(?P<ref>[^"]*)">'
    r'|<attachment name="(?P<name>[^"]*)">\n(?P<text>.*?)\n</attachment>)',
    re.DOTALL,
)

_IMAGE_OMITTED = "[Image {name} omitted: the selected model does not support images]"
_IMAGE_MISSING = "[Image {name} is no longer available]"


def read_text_attachment(name: str, data: bytes) -> str:
    """Decode an uploaded file as UTF-8 text.

    Args:
        name: File name (used in error messages)
        data: Raw file bytes

    Returns:
        str: The file content

    Raises:
        ValueError: If the file is too large ("too_large") or not UTF-8 text
            ("not_text"); the message is the reason code
    """
    if len(data) > ATTACHMENT_MAX_SIZE_KB * 1024:
        raise ValueError("too_large")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("not_text")


def validate_image_attachment(data: bytes) -> None:
    """Check that uploaded bytes are an image within the size limit.

    Args:
        data: Raw file bytes

    Raises:
        ValueError: If the file is too large ("image_too_large") or not a
            readable image ("not_image"); the message is the reason code
    """
    if len(data) > IMAGE_MAX_SIZE_MB * 1024 * 1024:
        raise ValueError("image_too_large")
    try:
        PILImage.open(io.BytesIO(data)).verify()
    except Exception:
        raise ValueError("not_image")


def build_message_content(
    prompt: str, attachments: List[Attachment], images: List[ImageRef] = ()
) -> str:
    """Embed images and text attachments into a user message after the prompt.

    Args:
        prompt: Text typed by the user
        attachments: List of (file name, file text)
        images: List of (file name, stored image reference)

    Returns:
        str: Message content stored in the chat history
    """
    image_tags = [
        f'\n\n<image name="{html.escape(name, quote=True)}" '
        f'ref="{html.escape(ref, quote=True)}">'
        for name, ref in images
    ]
    blocks = [
        f'\n\n<attachment name="{html.escape(name, quote=True)}">\n{text}\n</attachment>'
        for name, text in attachments
    ]
    return prompt + "".join(image_tags) + "".join(blocks)


def split_message_content(
    content: str,
) -> Tuple[str, List[Attachment], List[ImageRef]]:
    """Split message content into the prompt, text attachments and images.

    Only a run of blocks that extends to the end of the content counts, so
    marker-like text typed inside a prompt is left alone.

    Args:
        content: Message content as produced by ``build_message_content()``

    Returns:
        tuple: (prompt, list of (file name, file text), list of
        (file name, image reference)); messages without blocks return their
        content unchanged and two empty lists
    """
    for candidate in _BLOCK_RE.finditer(content):
        attachments, images = [], []
        pos = candidate.start()
        while pos < len(content):
            match = _BLOCK_RE.match(content, pos)
            if not match:
                break
            if match.group("ref") is not None:
                images.append(
                    (
                        html.unescape(match.group("image_name")),
                        html.unescape(match.group("ref")),
                    )
                )
            else:
                attachments.append(
                    (html.unescape(match.group("name")), match.group("text"))
                )
            pos = match.end()
        if pos == len(content):
            return content[: candidate.start()], attachments, images
    return content, [], []


def to_api_content(content: str, images_supported: bool) -> Union[str, list]:
    """Convert stored message content into the content sent to the LLM.

    Text attachments stay embedded. Image references become ``image_url``
    parts (base64 data URLs) if the model supports images; otherwise, or if an
    image file is missing, a short text note replaces the image.

    Args:
        content: Stored message content
        images_supported: Whether the target model accepts image input

    Returns:
        str | list: The content unchanged if it has no images, else a text
        string (images not supported) or a list of content parts
    """
    from lib.storage.attachment_store import get_image_data_url

    prompt, attachments, images = split_message_content(content)
    if not images:
        return content

    text = build_message_content(prompt, attachments)
    if not images_supported:
        return text + "".join(
            f"\n\n{_IMAGE_OMITTED.format(name=name)}" for name, _ in images
        )

    image_parts, notes = [], ""
    for name, ref in images:
        url = get_image_data_url(ref)
        if url:
            image_parts.append({"type": "image_url", "image_url": {"url": url}})
        else:
            notes += f"\n\n{_IMAGE_MISSING.format(name=name)}"
    return [{"type": "text", "text": text + notes}] + image_parts
