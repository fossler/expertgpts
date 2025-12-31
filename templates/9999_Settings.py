"""Settings page for DeepAgents application."""

import os
from pathlib import Path
import streamlit as st
from utils.config_manager import ConfigManager


# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        pass


st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize session state variables."""
    # Initialize API key in session state (from environment if not set)
    if "deepseek_api_key" not in st.session_state:
        env_api_key = os.getenv("DEEPSEEK_API_KEY")
        st.session_state.deepseek_api_key = env_api_key or ""


def render_api_key_section():
    """Render the API Key management section."""
    st.subheader("🔑 API Key Configuration")

    env_api_key = os.getenv("DEEPSEEK_API_KEY")
    has_env_key = bool(env_api_key)

    # Current status
    col1, col2 = st.columns(2)

    with col1:
        if has_env_key:
            st.success("✅ API key loaded from .env file")
        else:
            st.info("💡 No .env file found")

    with col2:
        if st.session_state.deepseek_api_key:
            st.success("✅ API key is set and available to all experts")
        else:
            st.warning("⚠️ API key not set")

    st.divider()

    # API Key input
    api_key = st.text_input(
        "DeepSeek API Key",
        key="settings_api_key",
        type="password",
        value=st.session_state.deepseek_api_key if st.session_state.deepseek_api_key else "",
        help="Enter your API key. It will be shared across all expert pages.",
        placeholder="Enter your API key here",
    )

    # Update session state if user entered/changed the key
    if api_key and api_key != st.session_state.deepseek_api_key:
        st.session_state.deepseek_api_key = api_key
        st.success("✅ API key updated successfully!")
        st.rerun()

    st.caption("💡 **Tip**: For automatic loading, create a `.env` file in the project root with: `DEEPSEEK_API_KEY=your_key_here`")

    st.divider()

    # Resources links
    st.subheader("📚 Resources")
    st.caption("**Useful Links**")
    "[Get a DeepSeek API key](https://platform.deepseek.com/)"
    "[DeepSeek API Documentation](https://api-docs.deepseek.com/)"
    "[View the source code](https://github.com/yourusername/deepagents)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/yourusername/deepagents)"


def render_expert_management_section():
    """Render the Expert Management section."""
    st.subheader("🤖 Expert Management")

    config_manager = ConfigManager()
    experts = config_manager.list_experts()

    if not experts:
        st.info("🔍 No expert agents found. Create your first expert from the Home page!")
        return

    st.caption(f"Found {len(experts)} expert agent(s)")

    # Display experts in a table
    for idx, expert in enumerate(experts):
        with st.expander(f"📝 {expert['expert_name']}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**Expert ID:** `{expert['expert_id']}`")
                st.markdown(f"**Description:** {expert['description']}")

                # Show metadata if available
                metadata = expert.get('metadata', {})
                if metadata:
                    st.markdown("**Metadata:**")
                    for key, value in metadata.items():
                        st.caption(f"• {key}: {value}")

            with col2:
                st.markdown("**Settings**")
                st.caption(f"🌡️ Temperature: {expert.get('temperature', 'N/A')}")

                system_prompt = expert.get('system_prompt', '')
                if system_prompt:
                    prompt_preview = system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt
                    st.caption(f"📋 System Prompt: {prompt_preview}")
                else:
                    st.caption("📋 System Prompt: Auto-generated")

            with col3:
                st.markdown("**Actions**")
                delete_key = f"delete_{expert['expert_id']}"
                if st.button("🗑️ Delete", key=delete_key, use_container_width=True):
                    st.session_state[f"confirm_delete_{expert['expert_id']}"] = True

        # Confirmation dialog for deletion
        if st.session_state.get(f"confirm_delete_{expert['expert_id']}"):
            st.warning(f"⚠️ Are you sure you want to delete **{expert['expert_name']}**? This action cannot be undone!")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Yes, Delete", key=f"confirm_{expert['expert_id']}", type="primary"):
                    try:
                        # Delete the config file
                        config_file = Path(__file__).parent.parent / "configs" / f"{expert['expert_id']}.yaml"
                        if config_file.exists():
                            config_file.unlink()

                        # Delete the page file
                        page_file = Path(__file__).parent / f"*_{expert['safe_name']}.py"

                        st.success(f"✅ Expert '{expert['expert_name']}' deleted successfully!")
                        st.session_state[f"confirm_delete_{expert['expert_id']}"] = False
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error deleting expert: {str(e)}")

            with col2:
                if st.button("❌ Cancel", key=f"cancel_{expert['expert_id']}"):
                    st.session_state[f"confirm_delete_{expert['expert_id']}"] = False
                    st.rerun()


def render_danger_zone_section():
    """Render the Danger Zone section for destructive actions."""
    st.subheader("⚠️ Danger Zone")

    st.warning("⚠️ **Warning**: Actions in this section are irreversible and will delete all your data!")

    st.markdown("""
    **Reset Application** will:
    - Delete all expert configurations
    - Delete all expert pages
    - Reset to the default example experts
    """)

    if st.button("🔄 Reset Application to Factory Defaults", type="primary", use_container_width=True):
        st.session_state.confirm_reset = True

    if st.session_state.get("confirm_reset"):
        st.error("🚨 **FINAL WARNING**: This will delete all experts and reset the application!")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Yes, Reset Everything", key="confirm_reset_button", type="primary"):
                try:
                    config_manager = ConfigManager()

                    # Delete all configs
                    configs_dir = Path(__file__).parent.parent / "configs"
                    if configs_dir.exists():
                        for config_file in configs_dir.glob("*.yaml"):
                            config_file.unlink()

                    # Delete all expert pages (except Settings.py)
                    pages_dir = Path(__file__).parent
                    if pages_dir.exists():
                        for page_file in pages_dir.glob("*.py"):
                            if page_file.name != "9999_Settings.py":
                                page_file.unlink()

                    st.success("✅ Application reset successfully!")
                    st.info("🔄 Please restart the application or run `python3 setup_examples.py` to recreate default experts.")

                    st.session_state.confirm_reset = False
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error resetting application: {str(e)}")

        with col2:
            if st.button("❌ Cancel", key="cancel_reset_button"):
                st.session_state.confirm_reset = False
                st.rerun()


def render_about_section():
    """Render the About section."""
    st.subheader("ℹ️ About")

    st.markdown("""
    ### DeepAgents

    A multi-expert AI chat application built with Streamlit, powered by the DeepSeek API.

    **Version:** 1.0.0

    **Features:**
    - 🎯 Domain-specific expert AI agents
    - 🔧 Customizable experts
    - 🌡️ Adjustable temperature settings
    - 💾 Chat history management
    - 📋 Template-based page generation

    **Resources:**
    - [Get a DeepSeek API key](https://platform.deepseek.com/)
    - [DeepSeek API Documentation](https://api-docs.deepseek.com/)
    - [View the source code](https://github.com/yourusername/deepagents)
    """)


def main():
    """Main settings page entry point."""
    initialize_session_state()

    st.title("⚙️ Settings")

    # Tab-based navigation for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 API Key", "🤖 Expert Management", "⚠️ Danger Zone", "ℹ️ About"])

    with tab1:
        render_api_key_section()

    with tab2:
        render_expert_management_section()

    with tab3:
        render_danger_zone_section()

    with tab4:
        render_about_section()

    # Footer
    st.divider()
    st.caption("💡 **Tip:** Changes made here are applied immediately across all expert pages.")


if __name__ == "__main__":
    main()
