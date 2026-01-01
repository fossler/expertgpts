"""ExpertGPTs - Multi-Expert AI Chat Application.

A Streamlit application that provides access to multiple domain-specific
expert AI agents powered by DeepSeek API.

This is the main entry point using the newer st.navigation() approach.
"""

import streamlit as st
from pathlib import Path
from utils.page_generator import PageGenerator
from utils import secrets_manager


def initialize_session_state():
    """Initialize session state variables before navigation."""
    # Initialize add chat dialog state
    if "show_add_chat_dialog" not in st.session_state:
        st.session_state.show_add_chat_dialog = False

    # Initialize API key in session state (from secrets if not set)
    if "deepseek_api_key" not in st.session_state:
        # Try to get from st.secrets first (Streamlit's recommended way)
        try:
            secrets_api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
            st.session_state.deepseek_api_key = secrets_api_key or ""
        except Exception:
            # If secrets.toml doesn't exist or has errors, initialize as empty
            st.session_state.deepseek_api_key = ""

    # Handle navigation to newly created expert (after rerun)
    if st.session_state.get("pending_expert_page"):
        page_path = st.session_state.pending_expert_page
        # Clear the pending navigation to avoid infinite loop
        st.session_state.pending_expert_page = None
        st.switch_page(page_path)


def main():
    """Main application entry point using st.navigation()."""

    # Initialize session state before navigation
    initialize_session_state()

    # Define the home page with icon
    home = st.Page(
        "pages/1000_Home.py",
        title="Home",
        icon=":material/home:"
    )

    # Define Settings page
    settings = st.Page(
        "pages/9999_Settings.py",
        title="Settings",
        icon=":material/settings:"
    )

    # Dynamically load all expert pages
    page_generator = PageGenerator()
    page_list = page_generator.list_pages()

    # Create page objects for each expert
    expert_pages = []
    for page_info in page_list:
        page_path = Path("pages") / page_info["filename"]
        expert_pages.append(
            st.Page(
                str(page_path),
                title=page_info["expert_name"],
                icon=":material/psychology:"
            )
        )

    # Create page list: Home + Experts + Settings
    pages = [home] + expert_pages + [settings]

    # Set up navigation
    pg = st.navigation(pages)

    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()
