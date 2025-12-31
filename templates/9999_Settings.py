"""Settings page for DeepAgents application."""

import io
import os
import zipfile
from datetime import datetime
from pathlib import Path
import streamlit as st
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator


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
    # Initialize add chat dialog state
    if "show_add_chat_dialog" not in st.session_state:
        st.session_state.show_add_chat_dialog = False

    # Initialize active tab state
    if "settings_active_tab" not in st.session_state:
        st.session_state.settings_active_tab = 0  # Default to first tab (API Key)

    # Initialize API key in session state (from environment if not set)
    if "deepseek_api_key" not in st.session_state:
        env_api_key = os.getenv("DEEPSEEK_API_KEY")
        st.session_state.deepseek_api_key = env_api_key or ""

    # Handle navigation to newly created expert (after rerun)
    if st.session_state.get("pending_expert_page"):
        page_path = st.session_state.pending_expert_page
        # Clear the pending navigation to avoid infinite loop
        st.session_state.pending_expert_page = None
        st.switch_page(page_path)


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


def create_new_expert(
    chat_name: str,
    description: str,
    temperature: float,
    custom_system_prompt: str = None
):
    """Create a new expert agent.

    Args:
        chat_name: Name of the expert
        description: Description of expertise
        temperature: Temperature setting
        custom_system_prompt: Optional custom system prompt

    Returns:
        tuple: (expert_id, page_path)
    """
    # Initialize managers
    config_manager = ConfigManager()
    page_generator = PageGenerator()

    # Create configuration
    expert_id = config_manager.create_config(
        expert_name=chat_name,
        description=description,
        temperature=temperature,
        system_prompt=custom_system_prompt,
    )

    # Generate page
    page_path = page_generator.generate_page(
        expert_id=expert_id,
        expert_name=chat_name,
    )

    return expert_id, page_path


def render_add_chat_dialog():
    """Render the Add Chat dialog.

    This dialog allows users to create a new Domain Expert Agent by providing:
    - Chat Name
    - Agent Description
    - Temperature (default: 1.0)
    """
    if not st.session_state.show_add_chat_dialog:
        return

    st.title("➕ Add New Expert Chat")

    with st.form("add_chat_form"):
        st.subheader("Expert Configuration")

        # Chat Name
        chat_name = st.text_input(
            "Chat Name *",
            placeholder="e.g., Python Expert, Data Scientist, Legal Advisor",
            help="A descriptive name for the domain expert",
            max_chars=100,
        ).strip()

        # Agent Description
        description = st.text_area(
            "Agent Description *",
            placeholder="Describe the expert's domain, expertise, and capabilities...",
            help="Detailed description of what this expert specializes in",
            height="content",
            max_chars=1000,
        ).strip()

        # Temperature
        temperature = st.number_input(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Controls randomness in responses. Lower = more focused, Higher = more creative",
        )

        # Optional: Custom System Prompt
        with st.expander("Advanced: Custom System Prompt"):
            custom_system_prompt = st.text_area(
                "Custom System Prompt (Optional)",
                placeholder="Leave empty to auto-generate from description...",
                height="content",
                help="Provide a custom system prompt for this expert",
                max_chars=2000,
            ).strip()

        st.caption("* Required fields")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submit_button = st.form_submit_button("Create Expert", width="stretch", type="primary")

        with col2:
            cancel_button = st.form_submit_button("Cancel", width="stretch")

        # Handle form submission
        if submit_button:
            if not chat_name or not description:
                st.error("Please fill in all required fields.")
                return

            try:
                expert_id, page_path = create_new_expert(chat_name, description, temperature, custom_system_prompt)

                # Store the page path for navigation after rerun
                st.session_state.pending_expert_page = page_path
                st.session_state.show_add_chat_dialog = False

                st.success(f"✅ Expert '{chat_name}' created successfully!")
                st.info("🔄 Navigating to your new expert...")

                # Rerun to let Streamlit discover the new page
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error creating expert: {str(e)}")

        if cancel_button:
            st.session_state.show_add_chat_dialog = False
            st.rerun()


def render_edit_expert_dialog():
    """Render the Edit Expert dialog.

    This dialog allows users to edit an existing expert agent.
    Expert ID cannot be changed.
    """
    # Find which expert is being edited
    editing_expert_id = None
    for key in st.session_state:
        if key.startswith("editing_expert_") and st.session_state[key]:
            editing_expert_id = key.replace("editing_expert_", "")
            break

    if not editing_expert_id:
        return

    # Load the expert's config
    config_manager = ConfigManager()
    try:
        expert_config = config_manager.load_config(editing_expert_id)
    except FileNotFoundError:
        st.error(f"❌ Expert not found: {editing_expert_id}")
        # Clear the editing state
        for key in st.session_state:
            if key.startswith("editing_expert_"):
                st.session_state[key] = False
        st.rerun()
        return

    st.title(f"✏️ Edit Expert: {expert_config['expert_name']}")

    with st.form("edit_expert_form"):
        st.subheader("Expert Configuration")

        # Expert ID (read-only)
        st.text_input(
            "Expert ID",
            value=expert_config['expert_id'],
            disabled=True,
            help="Expert ID cannot be changed",
        )

        # Expert Name
        chat_name = st.text_input(
            "Expert Name *",
            value=expert_config['expert_name'],
            help="A descriptive name for the domain expert",
            max_chars=100,
        ).strip()

        # Agent Description
        description = st.text_area(
            "Agent Description *",
            value=expert_config['description'],
            help="Detailed description of what this expert specializes in",
            height="content",
            max_chars=1000,
        ).strip()

        # Temperature
        temperature = st.number_input(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=float(expert_config.get('temperature', 1.0)),
            step=0.1,
            help="Controls randomness in responses. Lower = more focused, Higher = more creative",
        )

        # System Prompt
        custom_system_prompt = st.text_area(
            "System Prompt",
            value=expert_config.get('system_prompt', ''),
            height="content",
            help="The system prompt for this expert",
            max_chars=2000,
        ).strip()

        st.caption("* Required fields")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submit_button = st.form_submit_button("Save Changes", width="stretch", type="primary")

        with col2:
            cancel_button = st.form_submit_button("Cancel", width="stretch")

        # Handle form submission
        if submit_button:
            if not chat_name or not description:
                st.error("Please fill in all required fields.")
                return

            try:
                # Update the config
                config_manager.update_config(
                    editing_expert_id,
                    {
                        "expert_name": chat_name,
                        "description": description,
                        "temperature": temperature,
                        "system_prompt": custom_system_prompt,
                    }
                )

                # Clear the editing state
                st.session_state[f"editing_expert_{editing_expert_id}"] = False

                st.success(f"✅ Expert '{chat_name}' updated successfully!")
                st.info("🔄 Refreshing...")

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error updating expert: {str(e)}")

        if cancel_button:
            # Clear the editing state
            st.session_state[f"editing_expert_{editing_expert_id}"] = False
            st.rerun()


def render_expert_management_section():
    """Render the Expert Management section."""
    st.subheader("🤖 Expert Management")

    # Add new chat button
    if st.button("➕ Add new Chat", type="primary", width="content"):
        st.session_state.show_add_chat_dialog = True
        st.rerun()

    st.divider()

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
                st.markdown("**Description:**")
                st.text_area(
                    "Description",
                    value=expert['description'],
                    height=None,
                    disabled=True,
                    key=f"desc_preview_{expert['expert_id']}",
                    label_visibility="collapsed",
                )

                # Show system prompt
                system_prompt = expert.get('system_prompt', '')
                if system_prompt:
                    st.markdown("**System Prompt:**")
                    # Display as read-only text area preview
                    st.text_area(
                        "System Prompt",
                        value=system_prompt,
                        height=None,
                        disabled=True,
                        key=f"preview_{expert['expert_id']}",
                        label_visibility="collapsed",
                    )
                else:
                    st.markdown("**System Prompt:** Auto-generated")

            with col2:
                st.markdown("**Settings**")
                st.caption(f"🌡️ Temperature: {expert.get('temperature', 'N/A')}")

                # Show metadata if available
                metadata = expert.get('metadata', {})
                if metadata:
                    st.markdown("**Metadata:**")
                    for key, value in metadata.items():
                        st.caption(f"• {key}: {value}")

            with col3:
                st.markdown("**Actions**")
                edit_key = f"edit_{expert['expert_id']}"
                if st.button("✏️ Edit", key=edit_key, width="stretch"):
                    st.session_state[f"editing_expert_{expert['expert_id']}"] = True
                    st.rerun()

                delete_key = f"delete_{expert['expert_id']}"
                if st.button("🗑️ Delete", key=delete_key, width="stretch"):
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


def get_configs_as_zip():
    """Create a zip file containing all expert configurations.

    Returns:
        bytes: Zip file content as bytes
    """
    configs_dir = Path(__file__).parent.parent / "configs"

    # Create a zip file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        if configs_dir.exists():
            for config_file in configs_dir.glob("*.yaml"):
                # Add each config file to the zip
                zip_file.write(config_file, config_file.name)

    # Reset buffer position to the beginning
    zip_buffer.seek(0)

    return zip_buffer.getvalue()


def render_danger_zone_section():
    """Render the Danger Zone section for destructive actions."""
    st.subheader("⚠️ Danger Zone")

    st.warning("⚠️ **Warning**: Actions in this section are irreversible and will delete all your data!")

    # Download configs section
    st.markdown("---")
    st.markdown("### 💾 Backup Expert Configurations")

    st.markdown("""
    **Download All Configurations** will:
    - Download all expert configuration files as a ZIP archive
    - Preserve your custom experts and their settings
    - Allow you to restore configurations later (manual import required)
    """)

    # Get the zip file content
    config_zip = get_configs_as_zip()

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"deepagents_configs_{timestamp}.zip"

    # Download button
    st.download_button(
        label="📥 Download All Configurations (ZIP)",
        data=config_zip,
        file_name=filename,
        mime="application/zip",
        width="content",
    )

    st.markdown("---")

    st.markdown("""
    **Reset Application** will:
    - Delete all expert configurations
    - Delete all expert pages
    - Reset to the default example experts
    """)

    if st.button("🔄 Reset Application to Factory Defaults", type="primary", width="content"):
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

    # Render edit expert dialog if active
    for key in st.session_state:
        if key.startswith("editing_expert_") and st.session_state[key]:
            render_edit_expert_dialog()
            return

    # Render add chat dialog if active
    if st.session_state.show_add_chat_dialog:
        render_add_chat_dialog()
        return

    st.title("⚙️ Settings")

    # Tab-based navigation for different settings sections (stateful)
    tabs = ["🔑 API Key", "🤖 Expert Management", "⚠️ Danger Zone", "ℹ️ About"]
    active_tab = st.segmented_control(
        "Settings Sections",
        options=tabs,
        default=tabs[st.session_state.settings_active_tab],
        label_visibility="collapsed",
    )

    # Update session state with the current tab
    st.session_state.settings_active_tab = tabs.index(active_tab)

    # Render the appropriate section based on active tab
    if tabs.index(active_tab) == 0:
        render_api_key_section()
    elif tabs.index(active_tab) == 1:
        render_expert_management_section()
    elif tabs.index(active_tab) == 2:
        render_danger_zone_section()
    elif tabs.index(active_tab) == 3:
        render_about_section()

    # Footer
    st.divider()
    st.caption("💡 **Tip:** Changes made here are applied immediately across all expert pages.")


if __name__ == "__main__":
    main()
