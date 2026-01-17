"""ExpertGPTs - Multi-Expert AI Chat Application.

A Streamlit application that provides access to multiple domain-specific
expert AI agents powered by DeepSeek API.

This is the main entry point using the newer st.navigation() approach.
"""

import sys
import subprocess
import streamlit as st
from pathlib import Path
from utils.page_generator import PageGenerator
from utils.session_state import initialize_shared_session_state, handle_pending_navigation
from utils.constants import EXAMPLE_EXPERTS_COUNT
from utils.i18n import i18n
from utils.helpers import translate_expert_name


def check_first_run():
    """Check if this is a first run (no expert pages exist).

    Returns True if setup should be run.
    """
    pages_dir = Path(__file__).parent / "pages"

    # Check if expert pages exist (excluding Home, Settings, and Help)
    if pages_dir.exists():
        expert_pages = [
            f for f in pages_dir.glob("*.py")
            if f.name not in ["1000_Home.py", "9998_Settings.py", "9999_Help.py"]
            and not f.name.startswith("_")
        ]
        return len(expert_pages) == 0

    return True


def run_first_time_setup():
    """Run first-time setup by calling scripts/setup.py."""
    project_root = Path(__file__).parent

    st.info("""
    🚀 **First Run Detected**

    Setting up ExpertGPTs with example expert agents...
    This will only happen once.
    """)

    try:
        result = subprocess.run(
            [sys.executable, "scripts/setup.py"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True
        )

        st.success("✅ Setup complete! Refreshing...")
        st.rerun()

    except subprocess.CalledProcessError as e:
        st.error(f"""
        ❌ **Setup Failed**

        {e.stderr}

        Please run manually: `python3 scripts/setup.py`
        """)


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

    # Check for first run (before navigation)
    if check_first_run():
        run_first_time_setup()
        return  # Wait for rerun after setup

    # Initialize session state before navigation
    initialize_session_state()

    # Define the home page with icon
    home = st.Page(
        "pages/1000_Home.py",
        title=i18n.t("nav.home"),
        icon=":material/home:"
    )

    # Define Settings page
    settings = st.Page(
        "pages/9998_Settings.py",
        title=i18n.t("nav.settings"),
        icon=":material/settings:"
    )

    # Define Help page
    help_page = st.Page(
        "pages/9999_Help.py",
        title=i18n.t("nav.help", default="Help"),
        icon=":material/help:"
    )

    # Dynamically load all expert pages
    page_generator = PageGenerator()
    page_list = page_generator.list_pages()

    # Create page objects for each expert
    expert_pages = []
    for page_info in page_list:
        page_path = Path("pages") / page_info["filename"]

        # Skip if page file doesn't exist (may have been deleted)
        if not page_path.exists():
            continue

        # Get expert name for navigation (with translation for default experts)
        expert_id = page_info["expert_id"]
        expert_name = page_info["expert_name"]

        # Translate default expert names if available
        translated_name = translate_expert_name(expert_name)

        expert_pages.append(
            st.Page(
                str(page_path),
                title=translated_name,
                icon=":material/psychology:"
            )
        )

    # Create page list: Home + Experts + Settings + Help
    pages = [home] + expert_pages + [settings, help_page]

    # Set up navigation
    pg = st.navigation(pages)

    # Handle navigation to newly created expert (after rerun)
    # Must be called after st.navigation() is set up
    handle_pending_navigation()

    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()
