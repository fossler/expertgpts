"""ExpertGPTs - Multi-Expert AI Chat Application.

A Streamlit application that provides access to multiple domain-specific
expert AI agents powered by DeepSeek API.

This is the main entry point using the newer st.navigation() approach.
"""

import streamlit as st
from pathlib import Path
from utils.page_generator import PageGenerator
from utils.session_state import initialize_shared_session_state, handle_pending_navigation


def initialize_session_state():
    """Initialize session state variables before navigation."""
    # Initialize shared session state (API key, etc.)
    initialize_shared_session_state()

    # Initialize add chat dialog state
    if "show_add_chat_dialog" not in st.session_state:
        st.session_state.show_add_chat_dialog = False


def main():
    """Main application entry point using st.navigation()."""

    # Set page configuration (must be first st command)
    st.set_page_config(
        page_title="ExpertGPTs",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="auto"
    )

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

    # Handle navigation to newly created expert (after rerun)
    # Must be called after st.navigation() is set up
    handle_pending_navigation()

    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()
