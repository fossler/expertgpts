"""Chat toolbox below the chat input, and rendering of user messages.

The toolbox is rendered inside ``st.bottom`` right after ``st.chat_input``, so
it stays pinned below the input. For now it only offers "Attach file".
"""

from pathlib import Path
from typing import List

import streamlit as st

from lib.i18n.i18n import i18n
from lib.shared.attachments import (
    Attachment,
    read_text_attachment,
    split_message_content,
)
from lib.shared.constants import ATTACHMENT_FILE_TYPES, ATTACHMENT_MAX_SIZE_KB
from lib.shared.helpers import sanitize_markdown_content

# File extensions whose st.code language name differs from the extension
_CODE_LANGUAGES = {
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "sh": "bash",
    "md": "markdown",
    "yml": "yaml",
    "cs": "csharp",
    "rs": "rust",
    "rb": "ruby",
    "h": "c",
}


def render_chat_toolbox(widget_key: str) -> List[Attachment]:
    """Render the toolbox row and return the attachments for the next message.

    Must be called inside ``with st.bottom:`` after ``st.chat_input`` so the
    toolbox appears below the input. Files that are too large or not UTF-8
    text are reported and skipped.

    Args:
        widget_key: Key for the file uploader; change it to clear the
            attachments (e.g. after a message was sent)

    Returns:
        list: Valid attachments as (file name, file text)
    """
    attachments = []
    with st.container(horizontal=True, vertical_alignment="center"):
        with st.popover(
            i18n.t("chat_toolbox.attach_file"),
            icon=":material/attach_file:",
            type="tertiary",
        ):
            files = st.file_uploader(
                i18n.t("chat_toolbox.attach_file"),
                type=ATTACHMENT_FILE_TYPES,
                accept_multiple_files=True,
                key=widget_key,
                label_visibility="collapsed",
            )
            st.caption(i18n.t("chat_toolbox.attach_help", size=ATTACHMENT_MAX_SIZE_KB))

        for file in files or []:
            try:
                attachments.append(
                    (file.name, read_text_attachment(file.name, file.getvalue()))
                )
            except ValueError as e:
                st.caption(
                    "⚠️ "
                    + i18n.t(
                        f"chat_toolbox.error_{e}",
                        name=file.name,
                        size=ATTACHMENT_MAX_SIZE_KB,
                    )
                )

        if attachments:
            st.caption(
                i18n.t(
                    "chat_toolbox.attached",
                    files=", ".join(name for name, _ in attachments),
                )
            )
    return attachments


def render_user_message(content: str) -> None:
    """Render a user message, showing embedded attachments as expanders.

    Args:
        content: Message content (may contain attachment blocks)
    """
    prompt, attachments = split_message_content(content)
    st.markdown(sanitize_markdown_content(prompt))
    for name, text in attachments:
        extension = Path(name).suffix.lstrip(".").lower()
        with st.expander(f"📎 {name}"):
            st.code(text, language=_CODE_LANGUAGES.get(extension, extension or None))
