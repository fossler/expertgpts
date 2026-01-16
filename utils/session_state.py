"""Session state management utilities for ExpertGPTs.

This module provides shared functions for initializing and managing
session state across all pages in the application.
"""

import streamlit as st
from typing import Optional
from utils.types import MessagesList
from utils.i18n import i18n


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
    from utils.constants import LLM_PROVIDERS, DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL, DEFAULT_THINKING_ENABLED

    # Initialize language with saved preference or auto-detection
    if "language" not in st.session_state:
        from utils.app_defaults_manager import get_language_preference, save_language_preference

        # Try to load saved preference first
        saved_lang = get_language_preference()

        if saved_lang:
            # Use saved preference
            st.session_state.language = saved_lang
        else:
            # No saved preference - auto-detect and save
            detected_lang = i18n.detect_system_language()
            st.session_state.language = detected_lang

            # Save detected language to app_defaults for next time
            save_language_preference(detected_lang)

    # Initialize API keys dictionary in session state (from secrets if not set)
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

        # Try to load all provider API keys from st.secrets
        for provider_key, provider_config in LLM_PROVIDERS.items():
            env_var = provider_config["api_key_env"]  # e.g., "DEEPSEEK_API_KEY"
            try:
                secrets_api_key = st.secrets.get(env_var, "")
                if secrets_api_key:
                    st.session_state.api_keys[provider_key] = secrets_api_key
            except Exception:
                # If secrets.toml doesn't exist or has errors, continue
                pass

    # Initialize default LLM settings in session state
    # Try to load from app_defaults.toml first, fall back to constants
    from utils.app_defaults_manager import get_llm_defaults

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
        from utils.constants import get_default_model_for_provider
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
