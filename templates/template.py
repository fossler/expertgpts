"""Domain Expert Agent Chat Template.

This template is used to generate individual expert pages.
Replace {{EXPERT_ID}} and {{EXPERT_NAME}} when generating new pages.
"""

import streamlit as st
from utils.config_manager import ConfigManager
from utils.llm_client import LLMClient
from utils.session_state import initialize_shared_session_state
from utils.token_manager import TokenManager
from utils.i18n import i18n
from utils.helpers import translate_expert_name
from utils.constants import (
    LLM_PROVIDERS,
    get_provider_display_name,
    get_model_display_name,
    get_max_tokens,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS,
    CONFIG_CACHE_TTL
)


# Expert Configuration
EXPERT_ID = "{{EXPERT_ID}}"
EXPERT_NAME = "{{EXPERT_NAME}}"


def initialize_session_state():
    """Initialize session state variables."""
    # Initialize shared state first (API key, navigation, etc.)
    initialize_shared_session_state()

    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    return messages_key


def validate_api_key(api_key: str) -> tuple:
    """Validate API key format before using.

    Args:
        api_key: API key to validate

    Returns:
        tuple: (is_valid, error_message)
        - (True, "") if valid
        - (False, error_message) if invalid
    """
    if not api_key:
        return False, i18n.t("errors.api_key_not_set")

    if len(api_key) < 20:
        return False, i18n.t("errors.api_key_invalid")

    # Generic validation - different providers have different formats
    return True, ""


@st.cache_data(ttl=CONFIG_CACHE_TTL, show_spinner="Loading expert configuration...")
def load_expert_config_cached(expert_id: str, cache_version: int = 0) -> dict:
    """Load and cache the expert configuration.

    Args:
        expert_id: Unique ID of the expert
        cache_version: Version to invalidate cache when config is edited

    Returns:
        Configuration dictionary
    """
    config_manager = ConfigManager()

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
    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(api_key: str, config: dict, messages_key: str):
    """Handle user input and generate assistant response.

    Args:
        api_key: Provider-specific API key
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get provider and model from config metadata
    metadata = config.get("metadata", {})
    provider = metadata.get("provider", "deepseek")
    model = metadata.get("model", "deepseek-chat")
    thinking_level = metadata.get("thinking_level", "none")

    if prompt := st.chat_input(i18n.t("home.chat_input_placeholder")):
        # Validate API key format
        is_valid, error_msg = validate_api_key(api_key)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        # Add user message to chat history
        st.session_state[messages_key].append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                # Get LLM client from pool (cached for performance)
                from utils.client_pool import get_cached_client
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

                # Get system prompt from config and inject language prefix
                # This ensures AI responds in the user's preferred language
                raw_system_prompt = config.get("system_prompt", "")
                language_prefix = i18n.get_language_prefix()
                system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"

                response = ""
                for chunk in client.chat_stream(
                    messages=api_messages,
                    temperature=api_temperature,
                    model=model,
                    system_prompt=system_prompt_with_lang,
                    thinking_level=thinking_level
                ):
                    response += chunk
                    message_placeholder.markdown(response + "▌")

                message_placeholder.markdown(response)

                # Add assistant response to chat history
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": response
                })

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
            except ValueError as e:
                error_msg = i18n.t("errors.api_response_error", error=str(e))
                message_placeholder.error(f"❌ {error_msg}")
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}"
                })
            except Exception as e:
                error_msg = i18n.t("errors.unexpected_error", type=type(e).__name__, message=str(e))
                message_placeholder.error(f"❌ {error_msg}")
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": f"❌ {error_msg}"
                })
            st.rerun()


def clear_chat_history(messages_key: str):
    """Clear the chat history for this expert.

    Args:
        messages_key: Session state key for this expert's messages
    """
    if st.sidebar.button(f"🗑️ {i18n.t('sidebar.clear_chat_history')}"):
        st.session_state[messages_key] = []
        st.rerun()


def display_model_settings(config: dict, messages_key: str):
    """Display editable model settings in the sidebar.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get provider and model from config metadata
    metadata = config.get("metadata", {})
    provider = metadata.get("provider", "deepseek")
    model = metadata.get("model", "deepseek-chat")
    thinking_level = metadata.get("thinking_level", "none")

    # Get cache version for dynamic widget keys (ensures fresh state after save)
    cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)

    # Display model settings (editable)
    st.sidebar.markdown(f"### ⚙️ {i18n.t('sidebar.model_settings')}")

    # Model selection (filtered by current provider)
    from utils.constants import LLM_PROVIDERS, get_default_model_for_provider
    model_options = list(LLM_PROVIDERS[provider]["models"].keys())
    current_model_index = model_options.index(model) if model in model_options else 0

    new_model = st.sidebar.selectbox(
        i18n.t("sidebar.model"),
        options=model_options,
        index=current_model_index,
        format_func=lambda x: get_model_display_name(provider, x),
        key=f"{EXPERT_ID}_model_selector_v{cache_version}"
    )

    # Thinking Mode Level (provider-specific)
    new_thinking_level = thinking_level
    if provider == "openai":
        effort_options = ["none", "low", "medium", "high", "xhigh"]
        effort_index = effort_options.index(thinking_level) if thinking_level in effort_options else 0
        new_thinking_level = st.sidebar.selectbox(
            i18n.t("sidebar.thinking_mode"),
            options=effort_options,
            index=effort_index,
            format_func=lambda x: x.capitalize(),
            key=f"{EXPERT_ID}_thinking_selector_v{cache_version}"
        )
    elif provider == "zai":
        thinking_options = [i18n.t("sidebar.disabled"), i18n.t("sidebar.enabled")]
        option_index = 1 if thinking_level and thinking_level != "none" else 0
        selected_option = st.sidebar.selectbox(
            i18n.t("sidebar.thinking_mode"),
            options=thinking_options,
            index=option_index,
            key=f"{EXPERT_ID}_thinking_selector_v{cache_version}"
        )
        new_thinking_level = "medium" if selected_option == i18n.t("sidebar.enabled") else "none"
    # DeepSeek: no thinking mode control

    # Temperature (editable, but disabled for OpenAI)
    current_temperature = config.get("temperature", 1.0)
    if provider == "openai":
        new_temperature = st.sidebar.number_input(
            i18n.t("sidebar.temperature"),
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.01,
            disabled=True,
            format="%.2f",
            key=f"{EXPERT_ID}_temperature_input_v{cache_version}"
        )
    else:
        new_temperature = st.sidebar.number_input(
            i18n.t("sidebar.temperature"),
            min_value=0.0,
            max_value=2.0,
            value=float(current_temperature),
            step=0.1,
            format="%.1f",
            key=f"{EXPERT_ID}_temperature_input_v{cache_version}"
        )

    # Display provider links below temperature
    if provider == "deepseek":
        st.sidebar.markdown("[Chat](https://chat.deepseek.com/) | [Platform](https://platform.deepseek.com/usage)")
    elif provider == "openai":
        st.sidebar.markdown("[Chat](https://chatgpt.com/) | [Platform](https://platform.openai.com/usage)")
    elif provider == "zai":
        st.sidebar.markdown("[Chat](https://chat.z.ai/) | [Platform](https://z.ai/manage-apikey/subscription)")

    # Save button if any setting changed
    if (new_model != model or
        new_thinking_level != thinking_level or
        new_temperature != float(current_temperature)):
        if st.sidebar.button(f"💾 {i18n.t('sidebar.save_settings')}", key=f"{EXPERT_ID}_save_settings_v{cache_version}", type="primary"):
            try:
                config_manager = ConfigManager()
                config_manager.update_config(
                    expert_id=EXPERT_ID,
                    updates={
                        "model": new_model,
                        "thinking_level": new_thinking_level,
                        "temperature": new_temperature
                    }
                )
                # Invalidate cache to force reload
                cache_key = f"cache_version_{EXPERT_ID}"
                st.session_state[cache_key] = st.session_state.get(cache_key, 0) + 1
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
    metadata = config.get("metadata", {})
    provider = metadata.get("provider", "deepseek")
    model = metadata.get("model", "deepseek-chat")

    # Get provider/model-specific max tokens
    max_tokens = get_max_tokens(provider, model)

    # Calculate usage statistics using TokenManager
    # Use system prompt with language prefix for accurate token counting
    raw_system_prompt = config.get("system_prompt", "")
    language_prefix = i18n.get_language_prefix()
    system_prompt = f"{language_prefix}\n\n{raw_system_prompt}"
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

    # Get provider and model from config metadata
    metadata = config.get("metadata", {})
    provider = metadata.get("provider", "deepseek")

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

    # Render main interface
    render_chat_interface(config, messages_key)

    # Handle user input
    handle_user_input(api_key, config, messages_key)


if __name__ == "__main__":
    main()
