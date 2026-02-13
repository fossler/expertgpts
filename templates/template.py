"""Domain Expert Agent Chat Template.

This template is used to generate individual expert pages.
Replace {{EXPERT_ID}} and {{EXPERT_NAME}} when generating new pages.
"""

import time
import streamlit as st
from pathlib import Path
from lib.config.config_manager import get_config_manager
from lib.config.config_manager import get_llm_metadata
from lib.llm import LLMClient, TokenManager
from lib.shared.session_state import initialize_shared_session_state
from lib.i18n import i18n
from lib.shared.helpers import translate_expert_name
from lib.storage import (
    load_chat_history,
    save_chat_history,
    delete_chat_history
)
from lib.shared import (
    LLM_PROVIDERS,
    get_provider_display_name,
    get_model_display_name,
    get_provider_avatar,
    get_provider_links,
    get_max_tokens,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS,
    CONFIG_CACHE_TTL
)
from lib.ui.dialogs import render_temperature_input, render_thinking_mode_ui, render_model_selection
from lib.shared.session_state import invalidate_expert_cache
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
            response = cache_file.read_text(encoding='utf-8')

            # Check for error marker
            if "[STREAMING ERROR:" in response:
                st.warning(f"⚠️ {i18n.t('errors.background_stream_error')}")
                # Extract error message if available
                if metadata_file.exists():
                    try:
                        metadata = read_json(metadata_file)
                        if metadata is not None:
                            error = metadata.get('error')
                            if error:
                                st.error(f"Error: {error}")
                    except Exception:
                        pass

                # Clean up error files
                cache_file.unlink(missing_ok=True)
                metadata_file.unlink(missing_ok=True)
                return True

            # Check if already in chat history (avoid duplicates)
            already_displayed = any(
                msg.get("content") == response
                for msg in st.session_state[messages_key]
            )

            if not already_displayed and response.strip():
                # Add to chat history
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": response
                })

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
        st.error(f"Error reading cached response: {str(e)}")
        try:
            cache_file.unlink(missing_ok=True)
            metadata_file.unlink(missing_ok=True)
        except Exception:
            pass

    return False


def poll_stream_and_display(cache: "StreamingCache", expert_id: str, messages_key: str, message_placeholder) -> str:
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
            st.error(f"Streaming error: {error_msg}")
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
    response = poll_stream_and_display(cache, expert_id, messages_key, message_placeholder)

    # Only add to chat history if response is not empty
    if response.strip():
        # Add assistant response to chat history
        st.session_state[messages_key].append({
            "role": "assistant",
            "content": response
        })

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
    expert_name = config.get('expert_name', EXPERT_NAME)
    translated_name = translate_expert_name(expert_name)

    st.title(f"🤖 {translated_name}")

    # Display expert description
    if config.get("description"):
        st.markdown(f"*{config['description']}*")
        st.divider()

    # Display chat messages
    provider, _, _ = get_llm_metadata(config)
    for message in st.session_state[messages_key]:
        if message["role"] == "assistant":
            avatar = get_provider_avatar(provider)
            with st.chat_message("assistant", avatar=avatar):
                st.markdown(message["content"])
        else:
            with st.chat_message("user"):
                st.markdown(message["content"])


def handle_user_input(api_key: str, config: dict, messages_key: str):
    """Handle user input and generate assistant response.

    Args:
        api_key: Provider-specific API key
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get provider and model from config metadata
    provider, model, thinking_level = get_llm_metadata(config)

    if prompt := st.chat_input(i18n.t("home.chat_input_placeholder")):
        # Validate API key format
        is_valid, error_msg = validate_api_key(api_key)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        # Add user message to chat history
        st.session_state[messages_key].append({"role": "user", "content": prompt})

        # Persist to file
        save_chat_history(EXPERT_ID, st.session_state[messages_key])

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        avatar = get_provider_avatar(provider)
        with st.chat_message("assistant", avatar=avatar):
            message_placeholder = st.empty()

            try:
                # Get LLM client from pool (cached for performance)
                from lib.llm.client_pool import get_cached_client
                client = get_cached_client(provider=provider, api_key=api_key)

                # Convert messages to format expected by API
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
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
                system_prompt_with_lang = i18n.get_system_prompt_with_language(raw_system_prompt)

                # Initialize streaming cache
                cache = StreamingCache(EXPERT_ID)

                # Start background thread with streaming to file
                cache.start_streaming_to_file(
                    client=client,
                    messages=api_messages,
                    temperature=api_temperature,
                    model=model,
                    system_prompt=system_prompt_with_lang,
                    thinking_level=thinking_level
                )

                # Poll cache file for updates (battery-optimized: file I/O)
                response = poll_stream_and_display(cache, EXPERT_ID, messages_key, message_placeholder)

                # Only add to chat history if response is not empty
                if response.strip():  # Prevent empty responses
                    # Add assistant response to chat history
                    st.session_state[messages_key].append({
                        "role": "assistant",
                        "content": response
                    })

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
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}"
                })
                # Persist to file
                save_chat_history(EXPERT_ID, st.session_state[messages_key])
            except ValueError as e:
                error_msg = i18n.t("errors.api_response_error", error=str(e))
                message_placeholder.error(f"❌ {error_msg}")
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}"
                })
                # Persist to file
                save_chat_history(EXPERT_ID, st.session_state[messages_key])
            except Exception as e:
                error_msg = i18n.t("errors.unexpected_error", type=type(e).__name__, message=str(e))
                message_placeholder.error(f"❌ {error_msg}")
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}"
                })
                # Persist to file
                save_chat_history(EXPERT_ID, st.session_state[messages_key])
            st.rerun()


def clear_chat_history(messages_key: str):
    """Clear the chat history for this expert.

    Clears both session state and persistent file storage.

    Args:
        messages_key: Session state key for this expert's messages
    """
    if st.sidebar.button(f"🗑️ {i18n.t('sidebar.clear_chat_history')}"):
        # Clear from session state
        st.session_state[messages_key] = []

        # Delete from file
        delete_chat_history(EXPERT_ID)

        st.rerun()


def display_model_settings(config: dict, messages_key: str):
    """Display editable model settings in the sidebar.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get provider and model from config metadata
    provider, model, thinking_level = get_llm_metadata(config)

    # Get cache version for dynamic widget keys (ensures fresh state after save)
    cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)

    # Display model settings (editable)
    st.sidebar.markdown(f"### ⚙️ {i18n.t('sidebar.model_settings')}")

    # Model selection (using shared helper)
    new_model = render_model_selection(
        provider=provider,
        current_model=model,
        widget_key=f"{EXPERT_ID}_model_selector_v{cache_version}",
        use_sidebar=True
    )

    # Thinking Mode Level (using shared helper)
    new_thinking_level = render_thinking_mode_ui(
        provider=provider,
        current_thinking=thinking_level,
        widget_key=f"{EXPERT_ID}_thinking_selector_v{cache_version}",
        use_sidebar=True
    )

    # Temperature (using shared helper)
    current_temperature = config.get("temperature", 1.0)
    new_temperature = render_temperature_input(
        value=float(current_temperature),
        provider=provider,
        use_sidebar=True,
        widget_key=f"{EXPERT_ID}_temperature_input_v{cache_version}",
        show_help=False
    )

    # Display provider links below temperature
    st.sidebar.markdown(get_provider_links(provider))

    # Save button if any setting changed
    if (new_model != model or
        new_thinking_level != thinking_level or
        new_temperature != float(current_temperature)):
        if st.sidebar.button(f"💾 {i18n.t('sidebar.save_settings')}", key=f"{EXPERT_ID}_save_settings_v{cache_version}", type="primary"):
            try:
                config_manager = get_config_manager()
                config_manager.update_config(
                    expert_id=EXPERT_ID,
                    updates={
                        "model": new_model,
                        "thinking_level": new_thinking_level,
                        "temperature": new_temperature
                    }
                )
                # Invalidate cache to force reload (using shared helper)
                invalidate_expert_cache(EXPERT_ID)
                st.success("✅ Settings saved successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error saving settings: {str(e)}")


def display_context_usage(config: dict, messages_key: str):
    """Display context length usage in the sidebar.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get provider and model from config metadata
    provider, model, _ = get_llm_metadata(config)

    # Get provider/model-specific max tokens
    max_tokens = get_max_tokens(provider, model)

    # Calculate usage statistics using TokenManager
    # Use system prompt with language prefix for accurate token counting
    raw_system_prompt = config.get("system_prompt", "")
    system_prompt = i18n.get_system_prompt_with_language(raw_system_prompt)
    messages = st.session_state.get(messages_key, [])

    try:
        stats = TokenManager.calculate_usage_statistics(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=max_tokens
        )
    except (ImportError, OSError, ValueError, TypeError) as e:
        st.sidebar.caption(f"ℹ️ Token counting unavailable: {type(e).__name__}")
        return

    if "error" in stats:
        st.sidebar.caption(f"ℹ️ {stats['error']}")
        return

    # Display context usage in sidebar
    st.sidebar.markdown(f"### 📊 {i18n.t('sidebar.context_usage')}")

    # Display main stats
    max_tokens_formatted = f"{stats['max_tokens']:,}"
    st.sidebar.markdown(
        f"{stats['color']} **{stats['usage_percent']:.1f}%** "
        f"{i18n.t('sidebar.of_tokens', max=max_tokens_formatted)}"
    )
    total_tokens_formatted = f"{stats['total_tokens']:,}"
    max_tokens_formatted = f"{stats['max_tokens']:,}"
    st.sidebar.caption(
        i18n.t('sidebar.total_tokens', total=total_tokens_formatted, max=max_tokens_formatted)
    )

    # Show breakdown
    with st.sidebar.expander(i18n.t("sidebar.see_breakdown")):
        st.caption(f"📝 {i18n.t('sidebar.system_prompt')}: {stats['system_tokens']:,} tokens")
        st.caption(f"💬 {i18n.t('sidebar.chat_messages')}: {stats['messages_tokens']:,} tokens")


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
        st.info(i18n.t('sidebar.go_to_settings_api_key', provider=provider_name))
        st.stop()

    # Display model settings (at the top of sidebar)
    display_model_settings(config, messages_key)

    st.sidebar.divider()

    # Clear chat button (in sidebar)
    clear_chat_history(messages_key)

    # Display context usage in sidebar (at the bottom)
    display_context_usage(config, messages_key)

    # Check for completed background streams (from cache files) FIRST
    # This ensures cached responses are loaded before rendering the interface
    check_and_display_cached_responses(config, messages_key)

    # Render main interface (will show any cached responses that were just loaded)
    render_chat_interface(config, messages_key)

    # Handle user input
    handle_user_input(api_key, config, messages_key)


if __name__ == "__main__":
    main()
