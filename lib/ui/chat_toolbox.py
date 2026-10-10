"""Chat toolbox below the chat input, and rendering of user messages.

The toolbox is rendered inside ``st.bottom`` right after ``st.chat_input``, so
it stays pinned below the input. The first row offers "Attach file", "Attach
image" and "Voice input" on the left, and "Clear chat history" and the context
usage on the right. The second row selects the model (all models of providers
with an API key) and its thinking mode / temperature.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

from lib.audio import (
    MAX_DURATION_SECONDS,
    TRANSCRIPTION_MODELS,
    get_audio_duration,
    get_transcription_provider,
    transcribe,
)
from lib.config.config_manager import get_config_manager, get_llm_metadata
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
    AUDIO_MAX_SIZE_MB,
    IMAGE_FILE_TYPES,
    IMAGE_MAX_SIZE_MB,
    LLM_PROVIDERS,
    get_fixed_temperature,
    get_max_temperature,
    get_max_tokens,
    get_model_config,
    get_model_display_name,
    get_provider_display_name,
    is_temperature_ignored,
    is_thinking_enabled,
    resolve_reasoning_effort,
    supports_images,
)
from lib.shared.helpers import sanitize_markdown_content
from lib.shared.session_state import invalidate_expert_cache
from lib.storage import delete_chat_history
from lib.storage.attachment_store import get_image_path

# (file name, image bytes) of an image attached but not yet sent
PendingImage = Tuple[str, bytes]


@dataclass
class ToolboxInput:
    """What the toolbox contributes to the next message.

    Attributes:
        attachments: Text attachments as (file name, file text)
        images: Images as (file name, image bytes), not yet stored
        voice_prompt: Transcribed voice message to send, if the user sent one
    """

    attachments: List[Attachment] = field(default_factory=list)
    images: List[PendingImage] = field(default_factory=list)
    voice_prompt: Optional[str] = None


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
) -> ToolboxInput:
    """Render the toolbox row and return its input for the next message.

    Must be called inside ``with st.bottom:`` after ``st.chat_input`` so the
    toolbox appears below the input. Invalid files are reported and skipped.

    Args:
        widget_key: Key prefix for the uploaders; change it to clear the
            attachments (e.g. after a message was sent)
        config: Expert configuration (provider, model, system prompt)
        expert_id: Unique expert identifier (for clearing the history)
        messages_key: Session state key of the expert's messages

    Returns:
        ToolboxInput: Attachments, images and an optional voice prompt
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

        # --- Voice input (speech-to-text) ---
        voice_prompt = _render_voice_input(widget_key, provider)

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

    # Second row: model, thinking mode, temperature
    _render_model_settings(config, expert_id)

    return ToolboxInput(attachments, images, voice_prompt)


def _model_options(current_provider: str, current_model: str) -> List[str]:
    """List "provider/model" options for all providers with an API key.

    Keeps the catalog order of ``LLM_PROVIDERS``. The expert's current model
    is always included so the selection stays valid.
    """
    api_keys = st.session_state.get("api_keys", {})
    options = [
        f"{provider}/{model}"
        for provider, provider_config in LLM_PROVIDERS.items()
        if api_keys.get(provider)
        for model in provider_config["models"]
    ]
    current = f"{current_provider}/{current_model}"
    if current not in options:
        options.insert(0, current)
    return options


def _mark_model_settings_changed(expert_id: str) -> None:
    """on_change callback: remember that the user changed a model setting."""
    st.session_state[f"{expert_id}_model_settings_changed"] = True


def _render_thinking_select(
    provider: str, model: str, current: Optional[str], key: str, expert_id: str
) -> str:
    """Render the thinking control that fits the model and return its level.

    - Models with reasoning efforts: effort selectbox (unsupported stored
      levels fall back to the model's default)
    - Models that always think (kimi-k2.7-code): nothing to choose
    - Older Z.AI models and KIMI K2.6: enabled/disabled
    """
    model_config = get_model_config(provider, model)
    label = i18n.t("sidebar.thinking_mode")
    efforts = model_config.get("reasoning_efforts")
    if efforts:
        return st.selectbox(
            label,
            efforts,
            index=efforts.index(resolve_reasoning_effort(provider, model, current)),
            format_func=lambda effort: f"🧠 {effort.capitalize()}",
            label_visibility="collapsed",
            width=140,
            key=key,
            on_change=_mark_model_settings_changed,
            args=(expert_id,),
        )
    if model_config.get("thinking_always_on"):
        return "medium"
    if provider in ("zai", "kimi"):
        enabled = st.selectbox(
            label,
            [False, True],
            index=int(bool(current) and current != "none"),
            format_func=lambda on: (
                "🧠 "
                + (i18n.t("sidebar.enabled") if on else i18n.t("sidebar.disabled"))
            ),
            label_visibility="collapsed",
            width=140,
            key=key,
            on_change=_mark_model_settings_changed,
            args=(expert_id,),
        )
        return "medium" if enabled else "none"
    return current or "none"


def _render_model_settings(config: dict, expert_id: str) -> None:
    """Render the model row and save changes to the expert config right away.

    Shows a dropdown with all models of providers that have an API key and,
    next to it, the thinking mode and temperature where the model allows
    them (fixed temperatures are hidden, temperatures the provider ignores
    while thinking are disabled). Selecting a model of another provider
    switches the expert's provider.

    Args:
        config: Expert configuration dictionary
        expert_id: Unique expert identifier
    """
    provider, model, thinking_level = get_llm_metadata(config)
    temperature = float(config.get("temperature", 1.0))
    version = st.session_state.get(f"cache_version_{expert_id}", 0)
    options = _model_options(provider, model)

    with st.container(horizontal=True, vertical_alignment="center"):
        choice = st.selectbox(
            i18n.t("sidebar.model"),
            options,
            index=options.index(f"{provider}/{model}"),
            format_func=lambda option: get_model_display_name(*option.split("/", 1)),
            label_visibility="collapsed",
            width=220,
            key=f"{expert_id}_toolbox_model_v{version}",
            on_change=_mark_model_settings_changed,
            args=(expert_id,),
        )
        new_provider, new_model = choice.split("/", 1)
        new_thinking = _render_thinking_select(
            new_provider,
            new_model,
            thinking_level,
            key=f"{expert_id}_toolbox_thinking_{choice}_v{version}",
            expert_id=expert_id,
        )
        new_temperature = temperature
        thinking = is_thinking_enabled(new_thinking)
        if get_fixed_temperature(new_provider, new_model, thinking) is None:
            # Z.AI caps the range at 1.0; DeepSeek ignores temperature while
            # thinking. The cap is part of the key so a value above it from
            # the previous provider doesn't stick in the widget.
            max_temperature = get_max_temperature(new_provider)
            ignored = is_temperature_ignored(new_provider, new_thinking)
            new_temperature = min(temperature, max_temperature)
            # The hint sits on the icon: a collapsed label hides the input's help
            st.markdown(
                ":material/device_thermostat:",
                width="content",
                help=(
                    i18n.t("dialogs.temperature.ignored_with_thinking")
                    if ignored
                    else None
                ),
            )
            new_temperature = st.number_input(
                i18n.t("forms.temperature"),
                min_value=0.0,
                max_value=max_temperature,
                value=new_temperature,
                step=0.1,
                format="%.1f",
                disabled=ignored,
                label_visibility="collapsed",
                width=120,
                key=f"{expert_id}_toolbox_temperature_{max_temperature}_v{version}",
                on_change=_mark_model_settings_changed,
                args=(expert_id,),
            )

    # Save only after a real user change (not when a stored level that the
    # model doesn't support is merely displayed as the model's default)
    if st.session_state.pop(f"{expert_id}_model_settings_changed", False):
        get_config_manager().update_config(
            expert_id=expert_id,
            updates={
                "provider": new_provider,
                "model": new_model,
                "thinking_level": new_thinking,
                "temperature": new_temperature,
            },
        )
        invalidate_expert_cache(expert_id)
        st.rerun()


def _render_voice_input(widget_key: str, chat_provider: str) -> Optional[str]:
    """Render "Voice input": record audio, transcribe it, send the text.

    OpenAI experts transcribe with OpenAI, all others with Z.AI GLM-ASR (see
    ``lib.audio.transcription``). The transcript is returned right away, so
    it is sent automatically like a typed prompt. Each recording is
    transcribed (and therefore sent) once: results are cached by audio hash,
    and the recorder key changes after the message was sent.

    Args:
        widget_key: Key prefix; changes after each sent message, which also
            resets the recorder
        chat_provider: The expert's chat provider

    Returns:
        str | None: The text to send, or None
    """
    provider = get_transcription_provider(chat_provider)
    model = TRANSCRIPTION_MODELS[provider]
    api_key = st.session_state.get("api_keys", {}).get(provider)

    with st.popover(
        i18n.t("chat_toolbox.voice_input"),
        icon=":material/mic:",
        type="tertiary",
    ):
        audio = st.audio_input(
            i18n.t("chat_toolbox.voice_input"),
            key=f"{widget_key}_voice",
            label_visibility="collapsed",
            disabled=not api_key,
        )
        st.caption(i18n.t("chat_toolbox.voice_help"))
        st.caption(i18n.t("chat_toolbox.voice_model", model=model))
        if not api_key:
            st.info(
                i18n.t(
                    "chat_toolbox.voice_key_missing",
                    provider=get_provider_display_name(provider),
                    model=model,
                )
            )
            return None
        if audio is None:
            return None

        data = audio.getvalue()
        if len(data) > AUDIO_MAX_SIZE_MB * 1024 * 1024:
            st.warning(
                i18n.t("chat_toolbox.error_audio_too_large", size=AUDIO_MAX_SIZE_MB)
            )
            return None
        max_seconds = MAX_DURATION_SECONDS[provider]
        duration = get_audio_duration(data)
        if max_seconds and duration and duration > max_seconds:
            st.warning(
                i18n.t(
                    "chat_toolbox.error_audio_too_long",
                    seconds=max_seconds,
                    model=model,
                )
            )
            return None

        # Transcribe each recording once; reruns must not call the model again
        result_key = f"{widget_key}_voice_{hashlib.sha256(data).hexdigest()[:16]}"
        if result_key not in st.session_state:
            with st.spinner(i18n.t("chat_toolbox.voice_transcribing")):
                st.session_state[result_key] = transcribe(
                    data,
                    chat_provider,
                    api_key,
                    mime_type=audio.type or "audio/wav",
                    language=st.session_state.get("language"),
                    context=i18n.t("chat_toolbox.voice_asr_context"),
                )
        result = st.session_state[result_key]
        if not result.success:
            st.error(i18n.t("chat_toolbox.voice_error", error=result.error))
            return None

        return result.text
    return None


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
