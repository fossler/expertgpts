"""Session state management utilities for ExpertGPTs.

This module provides shared functions for initializing and managing
session state across all pages in the application.
"""

import streamlit as st


def initialize_shared_session_state():
    """Initialize shared session state variables across all pages.

    This function should be called once at app startup to initialize
    session state variables that are shared across all pages, such as:
    - API keys for all providers
    - Navigation state
    - Dialog states
    - Default LLM settings

    The function uses a try-except pattern to gracefully handle cases
    where secrets.toml doesn't exist or has errors.
    """
    # Import LLM_PROVIDERS to get all provider keys
    from utils.constants import LLM_PROVIDERS, DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL, DEFAULT_THINKING_ENABLED

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

    # Backward compatibility: Initialize deepseek_api_key for legacy code
    if "deepseek_api_key" not in st.session_state:
        st.session_state.deepseek_api_key = st.session_state.api_keys.get("deepseek", "")

    # Initialize default LLM settings in session state
    if "default_provider" not in st.session_state:
        st.session_state.default_provider = DEFAULT_LLM_PROVIDER

    if "default_model" not in st.session_state:
        st.session_state.default_model = DEFAULT_LLM_MODEL

    if "default_thinking_enabled" not in st.session_state:
        st.session_state.default_thinking_enabled = DEFAULT_THINKING_ENABLED


def handle_pending_navigation():
    """Handle navigation to newly created expert (after rerun).

    This function checks if there's a pending navigation request and
    switches to the target page if found. Should be called after
    initialize_shared_session_state().
    """
    if st.session_state.get("pending_expert_page"):
        page_path = st.session_state.pending_expert_page
        # Clear the pending navigation to avoid infinite loop
        st.session_state.pending_expert_page = None
        st.switch_page(page_path)
