"""Session state management utilities for ExpertGPTs.

This module provides shared functions for initializing and managing
session state across all pages in the application.
"""

import streamlit as st
from typing import Optional
from lib.shared.types import MessagesList


def initialize_shared_session_state():
    """Initialize shared session state variables across all pages.

    This function should be called once at app startup to initialize
    session state variables that are shared across all pages, such as:
    - API keys for all providers
    - Navigation state
    - Dialog states
    - Default LLM settings
    - Language preference (auto-detected from system)

    The function uses a try-except pattern to gracefully handle cases
    where secrets.toml doesn't exist or has errors.

    Performance: Cached by Streamlit's session state mechanism, only
    executes once per session.
    """
    # Import LLM_PROVIDERS to get all provider keys
    from lib.shared.constants import LLM_PROVIDERS, DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL, DEFAULT_THINKING_ENABLED

    # Initialize language with saved preference or auto-detection
    if "language" not in st.session_state:
        from lib.config.app_defaults_manager import get_language_preference, save_language_preference

        # Try to load saved preference first
        saved_lang = get_language_preference()

        if saved_lang:
            # Use saved preference
            st.session_state.language = saved_lang
        else:
            # No saved preference - auto-detect and save
            from lib.i18n.i18n import i18n
            detected_lang = i18n.detect_system_language()
            st.session_state.language = detected_lang

            # Save detected language to app_defaults for next time
            save_language_preference(detected_lang)

    # Initialize API keys dictionary in session state (from secrets if not set)
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

        # Load all provider API keys from secrets.toml file only (no env var fallback)
        # This ensures API keys only come from explicit user configuration
        from lib.config.secrets_manager import get_all_provider_api_keys

        api_keys = get_all_provider_api_keys()
        for provider_key, api_key in api_keys.items():
            if api_key:
                st.session_state.api_keys[provider_key] = api_key

    # Initialize default LLM settings in session state
    # Try to load from app_defaults.toml first, fall back to constants
    from lib.config.app_defaults_manager import get_llm_defaults

    if "default_provider" not in st.session_state:
        llm_defaults = get_llm_defaults()
        st.session_state.default_provider = llm_defaults["provider"]
        st.session_state.default_model = llm_defaults["model"]
        st.session_state.default_thinking_level = llm_defaults["thinking_level"]
        st.session_state.default_thinking_enabled = DEFAULT_THINKING_ENABLED


def initialize_expert_session_state(expert_id: str) -> None:
    """Initialize session state for a specific expert.

    This function ensures that all required session state variables
    exist for a given expert, initializing them to default values if needed.

    Args:
        expert_id: The expert's unique identifier

    Note:
        This function is called by expert pages to initialize their
        specific session state variables without affecting other experts.
    """
    messages_key = f"messages_{expert_id}"

    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Initialize provider/model settings for this expert if not set
    provider_key = f"provider_{expert_id}"
    model_key = f"model_{expert_id}"
    thinking_key = f"thinking_{expert_id}"
    temp_key = f"temperature_{expert_id}"

    if provider_key not in st.session_state:
        # Use default provider from shared state or constants
        st.session_state[provider_key] = st.session_state.get(
            "default_provider",
            "deepseek"
        )

    if model_key not in st.session_state:
        # Use default model for the selected provider
        from lib.shared.constants import get_default_model_for_provider
        provider = st.session_state[provider_key]
        st.session_state[model_key] = get_default_model_for_provider(provider)

    if thinking_key not in st.session_state:
        st.session_state[thinking_key] = "none"

    if temp_key not in st.session_state:
        st.session_state[temp_key] = 1.0


def get_expert_messages(expert_id: str) -> MessagesList:
    """Get the message history for a specific expert.

    Args:
        expert_id: The expert's unique identifier

    Returns:
        List[Message]: The message history for this expert

    Note:
        Returns an empty list if the expert has no messages yet.
    """
    messages_key = f"messages_{expert_id}"
    return st.session_state.get(messages_key, [])


def get_expert_setting(expert_id: str, setting: str, default=None):
    """Get a session state setting for a specific expert.

    Args:
        expert_id: The expert's unique identifier
        setting: The setting key (e.g., "provider", "model", "temperature")
        default: Default value if setting doesn't exist

    Returns:
        The setting value or default
    """
    setting_key = f"{setting}_{expert_id}"
    return st.session_state.get(setting_key, default)


def set_expert_setting(expert_id: str, setting: str, value) -> None:
    """Set a session state setting for a specific expert.

    Args:
        expert_id: The expert's unique identifier
        setting: The setting key (e.g., "provider", "model", "temperature")
        value: The value to set
    """
    setting_key = f"{setting}_{expert_id}"
    st.session_state[setting_key] = value


def clear_expert_messages(expert_id: str) -> None:
    """Clear the message history for a specific expert.

    Args:
        expert_id: The expert's unique identifier
    """
    messages_key = f"messages_{expert_id}"
    if messages_key in st.session_state:
        del st.session_state[messages_key]


def handle_pending_navigation():
    """Handle navigation to newly created expert (after rerun).

    This function checks if there's a pending navigation request and
    switches to the target page if found. Should be called after
    initialize_shared_session_state().

    Note:
        This function clears the pending navigation after handling it
        to prevent infinite loops.
    """
    if st.session_state.get("pending_expert_page"):
        page_path = st.session_state.pending_expert_page
        # Clear the pending navigation to avoid infinite loop
        st.session_state.pending_expert_page = None
        st.switch_page(page_path)


def ensure_dialog_state(*dialog_names: str) -> None:
    """Ensure dialog state variables exist in session state.

    This helper function initializes multiple dialog state variables
    at once, reducing repetitive boilerplate code across pages.

    Args:
        *dialog_names: Names of dialog state variables to initialize
                      (e.g., "add_chat", "edit", "delete")

    Example:
        # Before (repetitive):
        if "show_add_chat_dialog" not in st.session_state:
            st.session_state.show_add_chat_dialog = False
        if "show_edit_dialog" not in st.session_state:
            st.session_state.show_edit_dialog = False
        if "show_delete_dialog" not in st.session_state:
            st.session_state.show_delete_dialog = False

        # After (using helper):
        ensure_dialog_state("add_chat", "edit", "delete")
    """
    for name in dialog_names:
        key = f"show_{name}_dialog"
        if key not in st.session_state:
            st.session_state[key] = False


def invalidate_expert_cache(expert_id: str) -> None:
    """Increment cache version for an expert to force config reload.

    This helper function centralizes cache invalidation logic, ensuring
    consistent behavior across all pages when expert configs are modified.

    Args:
        expert_id: The expert's unique identifier

    Example:
        # Before (inconsistent approaches):
        if f"cache_version_{expert_id}" not in st.session_state:
            st.session_state[f"cache_version_{expert_id}"] = 0
        st.session_state[f"cache_version_{expert_id}"] += 1

        # After (using helper):
        invalidate_expert_cache(expert_id)
    """
    cache_key = f"cache_version_{expert_id}"
    st.session_state[cache_key] = st.session_state.get(cache_key, 0) + 1
