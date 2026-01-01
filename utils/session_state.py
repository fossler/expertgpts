"""Session state management utilities for ExpertGPTs.

This module provides shared functions for initializing and managing
session state across all pages in the application.
"""

import streamlit as st


def initialize_shared_session_state():
    """Initialize shared session state variables across all pages.

    This function should be called once at app startup to initialize
    session state variables that are shared across all pages, such as:
    - API key configuration
    - Navigation state
    - Dialog states

    The function uses a try-except pattern to gracefully handle cases
    where secrets.toml doesn't exist or has errors.
    """
    # Initialize API key in session state (from secrets if not set)
    if "deepseek_api_key" not in st.session_state:
        # Try to get from st.secrets first (Streamlit's recommended way)
        try:
            secrets_api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
            st.session_state.deepseek_api_key = secrets_api_key or ""
        except Exception:
            # If secrets.toml doesn't exist or has errors, initialize as empty
            st.session_state.deepseek_api_key = ""


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
