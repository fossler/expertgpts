"""Text file attachments for chat messages.

Attached files are embedded into the user message content, so the LLM request,
token counting, chat history persistence and size limits all work unchanged.
Each file is wrapped in an ``<attachment name="...">`` block after the prompt;
``split_message_content()`` reverses this for display.
"""

import html
import re
from typing import List, Tuple

from lib.shared.constants import ATTACHMENT_MAX_SIZE_KB

# (file name, file text)
Attachment = Tuple[str, str]

_ATTACHMENT_RE = re.compile(
    r'\n\n<attachment name="(?P<name>[^"]*)">\n(?P<text>.*?)\n</attachment>',
    re.DOTALL,
)


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


def build_message_content(prompt: str, attachments: List[Attachment]) -> str:
    """Embed attachments into a user message after the prompt.

    Args:
        prompt: Text typed by the user
        attachments: List of (file name, file text)

    Returns:
        str: Message content sent to the LLM and stored in the chat history
    """
    blocks = [
        f'\n\n<attachment name="{html.escape(name, quote=True)}">\n{text}\n</attachment>'
        for name, text in attachments
    ]
    return prompt + "".join(blocks)


def split_message_content(content: str) -> Tuple[str, List[Attachment]]:
    """Split message content into the prompt and its embedded attachments.

    Args:
        content: Message content as produced by ``build_message_content()``

    Returns:
        tuple: (prompt, list of (file name, file text)); messages without
        attachments return their content unchanged and an empty list
    """
    first = _ATTACHMENT_RE.search(content)
    if not first:
        return content, []
    attachments = [
        (html.unescape(m.group("name")), m.group("text"))
        for m in _ATTACHMENT_RE.finditer(content, first.start())
    ]
    return content[: first.start()], attachments
