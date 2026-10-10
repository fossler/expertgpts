"""Chat toolbox below the chat input, and rendering of user messages.

The toolbox is rendered inside ``st.bottom`` right after ``st.chat_input``, so
it stays pinned below the input. It offers "Attach file" and "Attach image"
on the left, and "Clear chat history" and the context usage on the right.
"""

from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

from lib.config.config_manager import get_llm_metadata
from lib.i18n.i18n import i18n
from lib.llm import TokenManager
from lib.shared.attachments import (
    Attachment,
    read_text_attachment,
    split_message_content,
    validate_image_attachment,
)
from lib.shared.constants import (
    ATTACHMENT_FILE_TYPES,
    ATTACHMENT_MAX_SIZE_KB,
    IMAGE_FILE_TYPES,
    IMAGE_MAX_SIZE_MB,
    get_max_tokens,
    get_model_display_name,
    supports_images,
)
from lib.shared.helpers import sanitize_markdown_content
from lib.storage import delete_chat_history
from lib.storage.attachment_store import get_image_path

# (file name, image bytes) of an image attached but not yet sent
PendingImage = Tuple[str, bytes]

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


def render_chat_toolbox(
    widget_key: str, config: dict, expert_id: str, messages_key: str
) -> Tuple[List[Attachment], List[PendingImage]]:
    """Render the toolbox row and return the attachments for the next message.

    Must be called inside ``with st.bottom:`` after ``st.chat_input`` so the
    toolbox appears below the input. Invalid files are reported and skipped.

    Args:
        widget_key: Key prefix for the uploaders; change it to clear the
            attachments (e.g. after a message was sent)
        config: Expert configuration (provider, model, system prompt)
        expert_id: Unique expert identifier (for clearing the history)
        messages_key: Session state key of the expert's messages

    Returns:
        tuple: (text attachments as (name, text), images as (name, bytes))
    """
    provider, model, _ = get_llm_metadata(config)
    messages = st.session_state.get(messages_key, [])
    attachments, images, notes = [], [], []

    with st.container(horizontal=True, vertical_alignment="center"):
        # --- Attach file (text) ---
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
                notes.append(_error_note(e, file.name))

        # --- Attach image (only for models that accept images) ---
        images_supported = supports_images(provider, model)
        with st.popover(
            i18n.t("chat_toolbox.attach_image"),
            icon=":material/image:",
            type="tertiary",
            disabled=not images_supported,
            help=None
            if images_supported
            else i18n.t(
                "chat_toolbox.image_not_supported",
                model=get_model_display_name(provider, model),
            ),
        ):
            image_files = st.file_uploader(
                i18n.t("chat_toolbox.attach_image"),
                type=IMAGE_FILE_TYPES,
                accept_multiple_files=True,
                key=f"{widget_key}_images",
                label_visibility="collapsed",
            )
            st.caption(i18n.t("chat_toolbox.attach_image_help", size=IMAGE_MAX_SIZE_MB))

        if images_supported:
            for file in image_files or []:
                data = file.getvalue()
                try:
                    validate_image_attachment(data)
                    images.append((file.name, data))
                except ValueError as e:
                    notes.append(_error_note(e, file.name))

        # --- Status: skipped files and current attachments ---
        for note in notes:
            st.caption(f"⚠️ {note}")
        if attachments:
            st.caption(
                i18n.t(
                    "chat_toolbox.attached",
                    files=", ".join(name for name, _ in attachments),
                )
            )
        if images:
            st.caption(
                i18n.t(
                    "chat_toolbox.attached_images",
                    files=", ".join(name for name, _ in images),
                )
            )

        # --- Right-aligned: clear chat history, context usage ---
        st.space("stretch")
        _render_clear_history(expert_id, messages_key, has_messages=bool(messages))
        _render_context_usage(config, messages)

    return attachments, images


def _error_note(error: ValueError, name: str) -> str:
    """Translate an attachment validation error into a toolbox note."""
    return i18n.t(
        f"chat_toolbox.error_{error}",
        name=name,
        size=IMAGE_MAX_SIZE_MB
        if str(error) == "image_too_large"
        else ATTACHMENT_MAX_SIZE_KB,
    )


def _render_clear_history(
    expert_id: str, messages_key: str, has_messages: bool
) -> None:
    """Render "Clear chat history" as a popover with a confirmation button.

    Deletes the persisted history and the expert's images, then reruns.

    Args:
        expert_id: Unique expert identifier
        messages_key: Session state key of the expert's messages
        has_messages: Whether there is anything to clear (disables otherwise)
    """
    with st.popover(
        i18n.t("sidebar.clear_chat_history"),
        icon=":material/delete:",
        type="tertiary",
        disabled=not has_messages,
    ):
        st.caption(i18n.t("chat_toolbox.clear_confirm"))
        if st.button(
            i18n.t("chat_toolbox.clear_button"),
            type="primary",
            key=f"clear_history_{expert_id}",
        ):
            st.session_state[messages_key] = []
            delete_chat_history(expert_id)
            st.rerun()


def _calculate_context_stats(config: dict, messages: list) -> Optional[dict]:
    """Calculate the context usage of the conversation.

    Args:
        config: Expert configuration dictionary
        messages: Current chat messages

    Returns:
        dict | None: TokenManager statistics, or None if counting failed
    """
    provider, model, _ = get_llm_metadata(config)
    # Use system prompt with language prefix for accurate token counting
    system_prompt = i18n.get_system_prompt_with_language(
        config.get("system_prompt", "")
    )
    try:
        stats = TokenManager.calculate_usage_statistics(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=get_max_tokens(provider, model),
        )
    except (ImportError, OSError, ValueError, TypeError):
        return None
    return None if "error" in stats else stats


def _render_context_usage(config: dict, messages: list) -> None:
    """Render the context usage as a compact popover with details.

    Args:
        config: Expert configuration dictionary
        messages: Current chat messages
    """
    stats = _calculate_context_stats(config, messages)
    if stats is None:
        st.caption(f"ℹ️ {i18n.t('sidebar.context_usage')}: –")
        return

    with st.popover(
        f"{stats['color']} {stats['usage_percent']:.1f}%",
        type="tertiary",
        help=i18n.t("sidebar.context_usage"),
    ):
        st.metric(
            label=i18n.t("sidebar.context_usage"),
            value=f"{stats['usage_percent']:.1f}%",
            delta=i18n.t(
                "sidebar.total_tokens",
                total=f"{stats['total_tokens']:,}",
                max=f"{stats['max_tokens']:,}",
            ),
            delta_color="off",
        )
        st.caption(
            f"📝 {i18n.t('sidebar.system_prompt')}: {stats['system_tokens']:,} tokens"
        )
        st.caption(
            f"💬 {i18n.t('sidebar.chat_messages')}: {stats['messages_tokens']:,} tokens"
        )


def render_user_message(content: str) -> None:
    """Render a user message with its images and text attachments.

    Args:
        content: Message content (may contain image tags and attachment blocks)
    """
    prompt, attachments, images = split_message_content(content)
    st.markdown(sanitize_markdown_content(prompt))

    if images:
        with st.container(horizontal=True):
            for name, ref in images:
                path = get_image_path(ref)
                if path:
                    st.image(str(path), width=240, alt=name)
                else:
                    st.caption(f"🖼️ {name} ({i18n.t('chat_toolbox.image_unavailable')})")

    for name, text in attachments:
        extension = Path(name).suffix.lstrip(".").lower()
        with st.expander(f"📎 {name}"):
            st.code(text, language=_CODE_LANGUAGES.get(extension, extension or None))
