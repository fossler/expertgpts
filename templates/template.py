"""Domain Expert Agent Chat Template.

This template is used to generate individual expert pages.
Replace {{EXPERT_ID}} and {{EXPERT_NAME}} when generating new pages.
"""

import time
import streamlit as st
from pathlib import Path
from lib.config.config_manager import get_config_manager
from lib.config.config_manager import get_llm_metadata
from lib.llm import LLMClient
from lib.shared.session_state import initialize_shared_session_state
from lib.i18n import i18n
from lib.shared.helpers import (
    translate_expert_name,
    sanitize_error_message,
    sanitize_markdown_content,
    add_error_to_history,
    render_git_branch_footer,
)
from lib.storage import load_chat_history, save_chat_history
from lib.storage.chat_history_manager import assistant_message
from lib.shared import (
    LLM_PROVIDERS,
    get_provider_display_name,
    get_model_display_name,
    get_provider_avatar,
    CONFIG_CACHE_TTL,
)
from lib.ui.chat_toolbox import render_chat_toolbox, render_user_message
from lib.shared.attachments import build_message_content, to_api_content
from lib.shared.constants import supports_images
from lib.storage.attachment_store import save_image
from lib.shared.format_ops import read_json
from lib.shared.helpers import validate_api_key
from lib.storage import StreamingCache

# Expert Configuration
EXPERT_ID = "{{EXPERT_ID}}"
EXPERT_NAME = "{{EXPERT_NAME}}"


def initialize_session_state():
    """Initialize session state variables.

    Loads chat history from file on first run, ensuring persistence
    across app restarts.
    """
    # Initialize shared state first (API key, navigation, etc.)
    initialize_shared_session_state()

    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        # Load from file if exists, otherwise start empty
        st.session_state[messages_key] = load_chat_history(EXPERT_ID)

    return messages_key


@st.cache_data(ttl=CONFIG_CACHE_TTL, show_spinner="Loading expert configuration...")
def load_expert_config_cached(expert_id: str, cache_version: int = 0) -> dict:
    """Load and cache the expert configuration.

    Args:
        expert_id: Unique ID of the expert
        cache_version: Version to invalidate cache when config is edited

    Returns:
        Configuration dictionary
    """
    config_manager = get_config_manager()

    try:
        config = config_manager.load_config(expert_id)
        return config
    except FileNotFoundError:
        return {}


def load_expert_config() -> dict:
    """Load the expert configuration with cache support.

    Returns:
        Configuration dictionary
    """
    # Get cache version from session state (incremented when config is edited)
    cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)

    config = load_expert_config_cached(EXPERT_ID, cache_version)

    if not config:
        st.error(f"❌ {i18n.t('errors.expert_config_not_found', expert_id=EXPERT_ID)}")

    return config


def check_and_display_cached_responses(config: dict, messages_key: str) -> bool:
    """Check for and display cached responses from background streams.

    This function is called on page load to detect if any background streams
    completed while the user was navigating away.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages

    Returns:
        True if cached responses were found or if polling is in progress
    """
    cache_dir = Path("streaming_cache")
    if not cache_dir.exists():
        return False

    # Check for the fixed "latest" cache file for this expert
    expert_id = config.get("expert_id", "")
    cache_file = cache_dir / f"{expert_id}_latest.txt"
    metadata_file = cache_dir / f"{expert_id}_latest.meta"

    if not cache_file.exists():
        return False

    try:
        # Check if streaming is complete
        is_complete = False
        has_error = False
        if metadata_file.exists():
            try:
                metadata = read_json(metadata_file)
                if metadata is not None:
                    is_complete = metadata.get("status") == "complete"
                    has_error = metadata.get("status") == "error"
            except Exception:
                pass

        # Handle completed streams
        if is_complete:
            response = cache_file.read_text(encoding="utf-8")

            # Check for error marker
            if "[STREAMING ERROR:" in response:
                st.warning(f"⚠️ {i18n.t('errors.background_stream_error')}")
                # Extract error message if available
                if metadata_file.exists():
                    try:
                        metadata = read_json(metadata_file)
                        if metadata is not None:
                            error = metadata.get("error")
                            if error:
                                st.error(f"Error: {sanitize_error_message(error)}")
                    except Exception:
                        pass

                # Clean up error files
                cache_file.unlink(missing_ok=True)
                metadata_file.unlink(missing_ok=True)
                return True

            # Check if already in chat history (avoid duplicates)
            already_displayed = any(
                msg.get("content") == response for msg in st.session_state[messages_key]
            )

            if not already_displayed and response.strip():
                # Add to chat history, attributed to the LLM that produced it
                origin = read_json(metadata_file) if metadata_file.exists() else None
                config_provider, config_model, _ = get_llm_metadata(config)
                st.session_state[messages_key].append(
                    assistant_message(
                        response,
                        (origin or {}).get("provider") or config_provider,
                        (origin or {}).get("model") or config_model,
                    )
                )

                # Save to persistent chat history
                save_chat_history(expert_id, st.session_state[messages_key])

                # Show notification
                st.success(f"✅ {i18n.t('success.background_stream_complete')}")

                # Clean up cache files
                cache_file.unlink(missing_ok=True)
                metadata_file.unlink(missing_ok=True)

                # Trigger rerun to display the new message
                st.rerun()
                return True

        # Handle incomplete streams - start polling
        elif not is_complete and not has_error:
            # Stream is still in progress, start polling for it
            poll_incomplete_stream(expert_id, messages_key)
            return True

    except Exception as e:
        # Log error and clean up corrupt file
        st.error(f"Error reading cached response: {sanitize_error_message(str(e))}")
        try:
            cache_file.unlink(missing_ok=True)
            metadata_file.unlink(missing_ok=True)
        except Exception:
            pass

    return False


def poll_stream_and_display(
    cache: "StreamingCache", expert_id: str, messages_key: str, message_placeholder
) -> str:
    """Poll cache file and display streaming response.

    This is a shared function used by both new streams and resumed streams.

    Args:
        cache: StreamingCache instance
        expert_id: Expert identifier
        messages_key: Session state key for messages
        message_placeholder: Streamlit empty container for updates

    Returns:
        Final response text
    """
    response = ""
    start_time = time.time()
    timeout = 300  # 5 minutes max

    while time.time() - start_time < timeout:
        # Read current cache content
        current = cache.read_cache()

        # Update display if cache has new content
        if current != response:
            response = current
            message_placeholder.markdown(response + "▌")

        # Check if streaming is complete
        if cache.is_complete():
            break

        # Check for errors
        if cache.has_error():
            error_msg = cache.get_error()
            st.error(f"Streaming error: {sanitize_error_message(error_msg)}")
            break

        # Small delay to avoid busy waiting (battery optimization)
        time.sleep(0.1)  # 100ms

    # Final display (remove cursor)
    message_placeholder.markdown(response)

    return response


def poll_incomplete_stream(expert_id: str, messages_key: str) -> None:
    """Poll and display an incomplete stream from background thread.

    This function is called when the user navigates back to a page
    where a background stream is still in progress.

    Args:
        expert_id: Expert identifier
        messages_key: Session state key for messages
    """
    from lib.storage.streaming_cache import StreamingCache

    # Create a cache instance to reuse its methods
    cache = StreamingCache(expert_id)

    # Create a message placeholder for real-time updates
    message_placeholder = st.empty()

    # Poll and display the stream
    response = poll_stream_and_display(
        cache, expert_id, messages_key, message_placeholder
    )

    # Only add to chat history if response is not empty
    if response.strip():
        # Add assistant response, attributed to the LLM that produced it
        st.session_state[messages_key].append(
            assistant_message(response, *cache.get_llm_origin())
        )

        # Persist to file
        save_chat_history(expert_id, st.session_state[messages_key])

        # Clean up cache files
        cache.cleanup()

        # Rerun to update context usage with new message
        st.rerun()


def render_chat_interface(config: dict, messages_key: str):
    """Render the main chat interface.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Translate expert name for default experts
    expert_name = config.get("expert_name", EXPERT_NAME)
    translated_name = translate_expert_name(expert_name)

    st.title(f"🤖 {translated_name}")

    # Display expert description
    if config.get("description"):
        st.markdown(f"*{config['description']}*")
        st.divider()

    # Display chat messages. Each answer shows the avatar of the provider that
    # produced it; older messages without that info use the current provider.
    provider, _, _ = get_llm_metadata(config)
    for message in st.session_state[messages_key]:
        if message["role"] == "assistant":
            avatar = get_provider_avatar(message.get("provider") or provider)
            with st.chat_message("assistant", avatar=avatar):
                st.markdown(sanitize_markdown_content(message["content"]))
        else:
            with st.chat_message("user"):
                render_user_message(message["content"])


def handle_user_input(api_key: str, config: dict, messages_key: str):
    """Handle user input and generate assistant response.

    Args:
        api_key: Provider-specific API key
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get provider and model from config metadata
    provider, model, thinking_level = get_llm_metadata(config)

    # Chat input with the toolbox (attachments, context usage) pinned below it.
    # The uploader keys change after each sent message to clear attachments.
    attachments_key = f"attachments_{EXPERT_ID}"
    attachments_generation = st.session_state.get(attachments_key, 0)
    with st.bottom:
        prompt = st.chat_input(i18n.t("home.chat_input_placeholder"))
        toolbox = render_chat_toolbox(
            f"{attachments_key}_{attachments_generation}",
            config,
            EXPERT_ID,
            messages_key,
        )

    # A transcribed voice message is sent like a typed prompt
    prompt = prompt or toolbox.voice_prompt
    if prompt:
        # Validate API key format with provider-specific validation
        is_valid, error_msg = validate_api_key(api_key, provider=provider)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        # Store images, embed attachments into the message, clear the toolbox
        image_refs = [
            (name, save_image(EXPERT_ID, name, data)) for name, data in toolbox.images
        ]
        content = build_message_content(prompt, toolbox.attachments, image_refs)
        st.session_state[attachments_key] = attachments_generation + 1

        # Add user message to chat history
        st.session_state[messages_key].append({"role": "user", "content": content})

        # Persist to file
        save_chat_history(EXPERT_ID, st.session_state[messages_key])

        # Display user message
        with st.chat_message("user"):
            render_user_message(content)

        # Generate assistant response
        avatar = get_provider_avatar(provider)
        with st.chat_message("assistant", avatar=avatar):
            message_placeholder = st.empty()

            try:
                # Get LLM client from pool (cached for performance)
                from lib.llm.client_pool import get_cached_client

                client = get_cached_client(provider=provider, api_key=api_key)

                # Convert messages to format expected by API (images become
                # image parts, or a text note if the model doesn't support them)
                images_supported = supports_images(provider, model)
                api_messages = [
                    {
                        "role": msg["role"],
                        "content": to_api_content(msg["content"], images_supported),
                    }
                    for msg in st.session_state[messages_key]
                ]

                # Stream response with provider/model-specific settings
                # OpenAI models only support temperature=1.0
                api_temperature = config.get("temperature", 1.0)
                if provider == "openai":
                    api_temperature = 1.0

                # Get system prompt with language prefix
                # This ensures AI responds in the user's preferred language
                raw_system_prompt = config.get("system_prompt", "")
                system_prompt_with_lang = i18n.get_system_prompt_with_language(
                    raw_system_prompt
                )

                # Initialize streaming cache
                cache = StreamingCache(EXPERT_ID)

                # Start background thread with streaming to file
                cache.start_streaming_to_file(
                    client=client,
                    messages=api_messages,
                    temperature=api_temperature,
                    model=model,
                    system_prompt=system_prompt_with_lang,
                    thinking_level=thinking_level,
                )

                # Poll cache file for updates (battery-optimized: file I/O)
                response = poll_stream_and_display(
                    cache, EXPERT_ID, messages_key, message_placeholder
                )

                # Only add to chat history if response is not empty
                if response.strip():  # Prevent empty responses
                    # Add assistant response to chat history
                    st.session_state[messages_key].append(
                        assistant_message(response, provider, model)
                    )

                    # Persist to file
                    save_chat_history(EXPERT_ID, st.session_state[messages_key])

                    # Clean up cache files
                    cache.cleanup()

                    # Rerun to update context usage with new message
                    st.rerun()

            except (ConnectionError, TimeoutError) as e:
                provider_name = get_provider_display_name(provider)
                error_msg = i18n.t("errors.network_error", provider_name=provider_name)
                message_placeholder.error(f"❌ {error_msg}")
                add_error_to_history(
                    EXPERT_ID, messages_key, error_msg, provider, model
                )
            except ValueError as e:
                error_msg = i18n.t(
                    "errors.api_response_error", error=sanitize_error_message(str(e))
                )
                message_placeholder.error(f"❌ {error_msg}")
                add_error_to_history(
                    EXPERT_ID, messages_key, error_msg, provider, model
                )
            except Exception as e:
                error_msg = i18n.t(
                    "errors.unexpected_error",
                    type=type(e).__name__,
                    message=sanitize_error_message(str(e)),
                )
                message_placeholder.error(f"❌ {error_msg}")
                add_error_to_history(
                    EXPERT_ID, messages_key, error_msg, provider, model
                )


def main():
    """Main application entry point."""
    messages_key = initialize_session_state()

    # Load expert configuration
    config = load_expert_config()

    if not config:
        st.error(i18n.t("sidebar.config_not_found", expert_id=EXPERT_ID))
        st.stop()

    # Get provider from config metadata
    provider, _, _ = get_llm_metadata(config)

    # Get provider-specific API key from session state
    api_keys = st.session_state.get("api_keys", {})
    api_key = api_keys.get(provider, "")

    if not api_key:
        provider_name = get_provider_display_name(provider)
        st.warning(f"⚠️ {i18n.t('sidebar.no_api_key_warning', provider=provider_name)}")
        st.info(i18n.t("sidebar.go_to_settings_api_key", provider=provider_name))
        st.stop()

    # Git branch footer in sidebar (at very bottom)
    render_git_branch_footer()

    # Check for completed background streams (from cache files) FIRST
    # This ensures cached responses are loaded before rendering the interface
    check_and_display_cached_responses(config, messages_key)

    # Render main interface (will show any cached responses that were just loaded)
    render_chat_interface(config, messages_key)

    # Handle user input
    handle_user_input(api_key, config, messages_key)


if __name__ == "__main__":
    main()
