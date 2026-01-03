"""Settings page for ExpertGPTs application."""

import io
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
import streamlit as st
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator
from utils.constants import EXPERT_BEHAVIOR_DOCS, EXPERT_BEHAVIOR_DOCS_EDIT
from utils.dialogs import create_new_expert, render_add_chat_dialog, render_temperature_input
from utils.helpers import sanitize_name
from utils import secrets_manager
from utils import config_toml_manager
from utils.session_state import initialize_shared_session_state, handle_pending_navigation


def initialize_session_state():
    """Initialize session state variables."""
    # Initialize shared session state (API key, navigation, etc.)
    initialize_shared_session_state()

    # Initialize add chat dialog state
    if "show_add_chat_dialog" not in st.session_state:
        st.session_state.show_add_chat_dialog = False

    # Initialize active tab state
    if "settings_active_tab" not in st.session_state:
        st.session_state.settings_active_tab = 0  # Default to first tab (API Key)

    # Handle navigation to newly created expert (after rerun)
    handle_pending_navigation()


def render_api_key_section():
    """Render the API Key management section."""
    st.subheader("🔑 API Key Configuration")

    has_file_key = secrets_manager.has_api_key_file()

    # Current status
    col1, col2 = st.columns(2)

    with col1:
        if has_file_key:
            st.success("✅ API key saved in secrets.toml")
        else:
            st.info("💡 No API key in secrets.toml")

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
        value="",  # Always show empty for security
        help="Enter your API key. It will be saved to .streamlit/secrets.toml and shared across all expert pages.",
        placeholder="Enter your API key here",
    )

    # Save button
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save API Key", type="primary", disabled=not api_key):
            try:
                # Save to secrets.toml file
                secrets_manager.save_api_key(api_key)

                # Update session state
                st.session_state.deepseek_api_key = api_key

                st.success("✅ API key saved successfully to .streamlit/secrets.toml!")
                st.info("🔄 The application will now rerun to load the new key.")

                # Rerun to load the new key from st.secrets
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving API key: {str(e)}")

    with col2:
        if st.button("🗑️ Clear API Key", disabled=not has_file_key):
            try:
                # Delete the secrets.toml file
                secrets_path = secrets_manager.get_secrets_path()
                if secrets_path.exists():
                    secrets_path.unlink()

                # Clear session state
                st.session_state.deepseek_api_key = ""

                st.success("✅ API key cleared successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error clearing API key: {str(e)}")

    st.divider()

    # Resources links
    st.subheader("📚 Resources")
    st.caption("**Useful Links**")
    "[Get a DeepSeek API key](https://platform.deepseek.com/)"
    "[DeepSeek API Documentation](https://api-docs.deepseek.com/)"
    "[View the source code](https://github.com/yourusername/expertgpts)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/yourusername/expertgpts)"


def render_general_settings_section():
    """Render the General Settings section for theme customization."""
    st.subheader("🎨 Theme Customization")

    st.caption("Customize the appearance of your ExpertGPTs application.")

    st.divider()

    # Define 7 complete themes with harmonious colors
    themes = {
        "Modern Red": {
            "primary": "#FF6B6B",
            "background": "#FFFFFF",
            "secondary": "#F0F2F6",
            "text": "#262730",
            "icon": "🔴"
        },
        "Ocean Blue": {
            "primary": "#4A90E2",
            "background": "#FFFFFF",
            "secondary": "#E8F0FE",
            "text": "#1E3A8A",
            "icon": "🔵"
        },
        "Forest Green": {
            "primary": "#10B981",
            "background": "#FFFFFF",
            "secondary": "#ECFDF5",
            "text": "#064E3B",
            "icon": "🟢"
        },
        "Royal Purple": {
            "primary": "#9B59B6",
            "background": "#FFFFFF",
            "secondary": "#F3E5F5",
            "text": "#4A148C",
            "icon": "🟣"
        },
        "Dark Blue": {
            "primary": "#4A90E2",
            "background": "#0E1117",
            "secondary": "#262730",
            "text": "#FAFAFA",
            "icon": "🌑"
        },
        "Dark Gray": {
            "primary": "#FF6B6B",
            "background": "#1A1A1A",
            "secondary": "#2D2D2D",
            "text": "#FFFFFF",
            "icon": "🖤"
        },
        "Custom": {
            "primary": "#F59E0B",
            "background": "#FFFBEB",
            "secondary": "#FEF3C7",
            "text": "#78350F",
            "icon": "🎨"
        }
    }

    # Create theme options with icons
    theme_options = [f"{icon} {name}" for name, theme in themes.items() for icon in [theme["icon"]]]
    theme_labels = {f"{theme['icon']} {name}": name for name, theme in themes.items()}

    # Initialize session state for selected theme and colors
    if "selected_theme_option" not in st.session_state:
        # Read current theme from config file (now includes theme_name!)
        current_config = config_toml_manager.get_theme_settings()

        # Get the saved theme name directly (defaults to "Custom" if not set)
        saved_theme_name = current_config.get("theme_name", "Custom")

        # Validate that the saved theme name exists in our predefined themes
        if saved_theme_name in themes and saved_theme_name != "Custom":
            # Use the saved theme directly - no color comparison needed!
            theme_data = themes[saved_theme_name]
            st.session_state.selected_theme_option = f"{theme_data['icon']} {saved_theme_name}"
            st.session_state.theme_primary_color = theme_data["primary"]
            st.session_state.theme_background_color = theme_data["background"]
            st.session_state.theme_secondary_background_color = theme_data["secondary"]
            st.session_state.theme_text_color = theme_data["text"]
        else:
            # Use Custom theme with current config values
            st.session_state.selected_theme_option = f"{themes['Custom']['icon']} Custom"
            st.session_state.theme_primary_color = current_config.get("primaryColor", "#F59E0B")
            st.session_state.theme_background_color = current_config.get("backgroundColor", "#FFFBEB")
            st.session_state.theme_secondary_background_color = current_config.get("secondaryBackgroundColor", "#FEF3C7")
            st.session_state.theme_text_color = current_config.get("textColor", "#78350F")

    # Radio button for theme selection (outside form for reactivity)
    selected_theme = st.radio(
        "Select a theme to preview",
        options=theme_options,
        index=theme_options.index(st.session_state.selected_theme_option),
        horizontal=True,
        key="theme_radio_selector"
    )

    # Extract theme name from selected option
    theme_name = theme_labels[selected_theme]
    theme_colors = themes[theme_name]

    # Update session state and rerun if selection changed
    if selected_theme != st.session_state.selected_theme_option:
        st.session_state.selected_theme_option = selected_theme
        # Update color values in session state
        st.session_state.theme_primary_color = theme_colors["primary"]
        st.session_state.theme_background_color = theme_colors["background"]
        st.session_state.theme_secondary_background_color = theme_colors["secondary"]
        st.session_state.theme_text_color = theme_colors["text"]
        st.rerun()

    st.divider()

    # Color Preview section (outside form for reactivity)
    st.markdown("### Color Preview")

    # Check if Custom theme is selected
    is_custom_theme = (theme_name == "Custom")

    # Create columns for color inputs in one row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        primary_color = st.color_picker(
            "Buttons and interactive Elements",
            value=st.session_state.theme_primary_color,
            help="Color for buttons and interactive elements",
            key=f"primary_{st.session_state.selected_theme_option}",
            disabled=not is_custom_theme
        )

    with col2:
        background_color = st.color_picker(
            "Background Color",
            value=st.session_state.theme_background_color,
            help="Main background color of the app",
            key=f"background_{st.session_state.selected_theme_option}",
            disabled=not is_custom_theme
        )

    with col3:
        secondary_background_color = st.color_picker(
            "Secondary Background",
            value=st.session_state.theme_secondary_background_color,
            help="Background color for sidebar and other secondary areas",
            key=f"secondary_{st.session_state.selected_theme_option}",
            disabled=not is_custom_theme
        )

    with col4:
        text_color = st.color_picker(
            "Text Color",
            value=st.session_state.theme_text_color,
            help="Main text color throughout the app",
            key=f"text_{st.session_state.selected_theme_option}",
            disabled=not is_custom_theme
        )

    # Update session state with current color picker values
    st.session_state.theme_primary_color = primary_color
    st.session_state.theme_background_color = background_color
    st.session_state.theme_secondary_background_color = secondary_background_color
    st.session_state.theme_text_color = text_color

    st.divider()

    # Check if we need to reload page (from Save & Apply button)
    # Note: We use switch_page() instead of rerun() because Streamlit only reads
    # config.toml on page load, not on rerun. This forces a complete page reload.
    if st.session_state.get("trigger_page_reload", False):
        st.session_state.trigger_page_reload = False
        # Switch to current page to force complete reload (re-reads config.toml)
        st.switch_page("pages/9999_Settings.py")

    # Single button to save and apply theme settings
    col1, col2, col3 = st.columns([2, 2, 4])

    def save_and_apply_theme():
        """Callback to save theme settings to config.toml and force page reload."""
        try:
            # Read current values directly from the color picker widgets
            primary_key = f"primary_{st.session_state.selected_theme_option}"
            background_key = f"background_{st.session_state.selected_theme_option}"
            secondary_key = f"secondary_{st.session_state.selected_theme_option}"
            text_key = f"text_{st.session_state.selected_theme_option}"

            # Get the current theme name (extract from radio selection)
            current_theme_name = theme_labels[st.session_state.selected_theme_option]

            # Save to config.toml
            config_toml_manager.save_theme_settings(
                theme_name=current_theme_name,
                primaryColor=st.session_state[primary_key],
                backgroundColor=st.session_state[background_key],
                secondaryBackgroundColor=st.session_state[secondary_key],
                textColor=st.session_state[text_key]
            )

            # Set flag to trigger page reload (not rerun!)
            st.session_state.trigger_page_reload = True

            # Show success toast
            st.toast("✅ Theme saved! Reloading page...", icon="🎨")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    with col1:
        if st.button("💾 Save & Apply Theme", key="save_apply_button", on_click=save_and_apply_theme, type="primary"):
            pass

    with col2:
        st.empty()  # Spacer

    with col3:
        st.empty()  # Spacer


def validate_expert_name(name: str) -> tuple[bool, str]:
    """Validate expert name contains only allowed characters.

    Allowed characters: A-Z, a-z, 0-9, underscore (_), hyphen (-), dot (.), space ( )

    Args:
        name: The expert name to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "Expert name cannot be empty"

    # Regex pattern for allowed characters
    pattern = r'^[A-Za-z0-9_.\- ]+$'

    if not re.match(pattern, name):
        allowed = "letters (A-Z, a-z), numbers (0-9), underscore (_), hyphen (-), dot (.), and space"
        return False, f"Expert name can only contain: {allowed}"

    return True, ""


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
            "Expert Name *",
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
        temperature = render_temperature_input()

        st.divider()

        # Expert Behavior (Advanced) - The most important field!
        st.markdown("### 🧠 Expert Behavior (Advanced)")
        st.caption(
            "💡 **This is the most important field!** It defines how your expert responds, thinks, and acts. "
            "Leave empty to auto-generate from description."
        )

        custom_system_prompt = st.text_area(
            "Customize Expert Behavior",
            placeholder="""How should this expert respond? (Optional)

Leave empty to auto-generate from description.

Example: "Provide clear, step-by-step explanations with code examples..." """,
            help="🎯 This defines everything about your expert - tone, expertise, style, and constraints",
            height=250,
            max_chars=3000,
        ).strip()

        # Add expander with examples
        with st.expander("📖 Why is this important? + Examples"):
            st.markdown(EXPERT_BEHAVIOR_DOCS)

        st.caption("* Required fields")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submit_button = st.form_submit_button("Create Expert", width="stretch", type="primary")

        with col2:
            cancel_button = st.form_submit_button("Cancel", width="stretch")

        # Handle form submission
        if submit_button:
            # Validate required fields
            if not chat_name or not description:
                st.error("Please fill in all required fields.")
                return

            # Validate expert name
            is_valid, error_msg = validate_expert_name(chat_name)
            if not is_valid:
                st.error(f"❌ {error_msg}")
                return

            try:
                # Get API key for system prompt generation
                api_key = st.session_state.get("deepseek_api_key", None)

                expert_id, page_path = create_new_expert(chat_name, description, temperature, custom_system_prompt, api_key)

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
        temperature = render_temperature_input(value=float(expert_config.get('temperature', 1.0)))

        st.divider()

        # Expert Behavior (Advanced) - The most important field!
        st.markdown("### 🧠 Expert Behavior (Advanced)")

        # Check if API key available
        api_key_available = bool(st.session_state.get("deepseek_api_key", ""))

        if api_key_available:
            caption_text = (
                "💡 **AI-powered generation!** Leave empty to regenerate a customized "
                "system prompt using AI. Provide your own for complete control."
            )
        else:
            caption_text = (
                "💡 **Manual mode**: API key not set, so AI generation is unavailable. "
                "Leave empty to keep the existing behavior, or provide your own."
            )

        st.caption(caption_text)

        custom_system_prompt = st.text_area(
            "Customize Expert Behavior",
            value=expert_config.get('system_prompt', ''),
            height=250,
            help="🎯 This defines everything about your expert - tone, expertise, style, and constraints",
            max_chars=3000,
        ).strip()

        # Add expander with examples
        with st.expander("📖 Why is this important? + Examples"):
            st.markdown(EXPERT_BEHAVIOR_DOCS_EDIT)

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
                # Determine if we need AI generation
                # Empty string means "regenerate with AI" (if API key available)
                # None means "keep existing"
                final_system_prompt = custom_system_prompt

                if custom_system_prompt == "" and api_key_available:
                    # User cleared the field - trigger AI regeneration
                    final_system_prompt = None

                elif custom_system_prompt == "" and not api_key_available:
                    # No API key - keep existing prompt
                    final_system_prompt = expert_config.get('system_prompt', '')

                # Get API key for AI generation
                api_key = st.session_state.get("deepseek_api_key", None) if api_key_available else None

                # Update the config
                config_manager.update_config(
                    editing_expert_id,
                    {
                        "expert_name": chat_name,
                        "description": description,
                        "temperature": temperature,
                        "system_prompt": final_system_prompt,
                        "api_key": api_key,
                    }
                )

                # Invalidate cache for this expert
                st.session_state[f"cache_version_{editing_expert_id}"] = st.session_state.get(f"cache_version_{editing_expert_id}", 0) + 1

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

    # Check API key availability
    api_key_available = st.session_state.get("deepseek_api_key", "")

    if api_key_available:
        if st.button("➕ Add new Chat", type="primary", width="content"):
            st.session_state.show_add_chat_dialog = True
            st.rerun()
    else:
        st.button(
            "➕ Add new Chat",
            type="primary",
            width="content",
            disabled=True,
            help="API key must be set to create new chats"
        )
        st.caption("⚠️ Set API key above to create experts")

    st.divider()

    # Load experts (not cached to avoid tab switching issues)
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

                # Show expert behavior
                system_prompt = expert.get('system_prompt', '')
                if system_prompt:
                    st.markdown("**🧠 Expert Behavior:**")
                    # Display as read-only text area preview
                    st.text_area(
                        "Expert Behavior",
                        value=system_prompt,
                        height=None,
                        disabled=True,
                        key=f"preview_{expert['expert_id']}",
                        label_visibility="collapsed",
                    )
                else:
                    st.markdown("**🧠 Expert Behavior:** Auto-generated from description")

            with col2:
                st.markdown("**Settings**")
                st.caption(f"🌡️ Temperature: {expert.get('temperature', 'N/A')}")

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
                        # Import PageGenerator
                        from utils.page_generator import PageGenerator

                        # Delete the config file using ConfigManager
                        config_manager = ConfigManager()
                        config_manager.delete_config(expert['expert_id'])

                        # Delete the page file using PageGenerator
                        page_generator = PageGenerator()
                        page_generator.delete_page(expert['expert_id'])

                        # Clear all cache for this expert
                        expert_id = expert['expert_id']

                        # Clear cache version
                        if f"cache_version_{expert_id}" in st.session_state:
                            del st.session_state[f"cache_version_{expert_id}"]

                        # Clear chat history for this expert
                        if f"messages_{expert_id}" in st.session_state:
                            del st.session_state[f"messages_{expert_id}"]

                        # Clear any other expert-specific state
                        keys_to_delete = [key for key in st.session_state.keys() if expert_id in str(key)]
                        for key in keys_to_delete:
                            del st.session_state[key]

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
    filename = f"expertgpts_configs_{timestamp}.zip"

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
                    # Delete all configs
                    configs_dir = Path(__file__).parent.parent / "configs"
                    if configs_dir.exists():
                        for config_file in configs_dir.glob("*.yaml"):
                            config_file.unlink()

                    # Delete all expert pages (except Home.py and Settings.py)
                    pages_dir = Path(__file__).parent
                    if pages_dir.exists():
                        for page_file in pages_dir.glob("*.py"):
                            # Keep core application files (Home and Settings)
                            if page_file.name not in ["1000_Home.py", "9999_Settings.py"]:
                                page_file.unlink()

                    # Recreate example experts using scripts/setup.py
                    st.info("🔄 Recreating example experts...")

                    # Run scripts/setup.py as a subprocess
                    result = subprocess.run(
                        [sys.executable, "scripts/setup.py"],
                        check=True,
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent.parent
                    )

                    st.success("✅ Application reset successfully!")
                    st.info("🔄 Restarting application...")

                    st.session_state.confirm_reset = False
                    st.rerun()

                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Error recreating experts: {e}")
                    if e.stdout:
                        st.error(f"Output: {e.stdout}")
                    if e.stderr:
                        st.error(f"Error: {e.stderr}")
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
    ### ExpertGPTs

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
    - [View the source code](https://github.com/yourusername/expertgpts)
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
    tabs = ["🎨 General", "🔑 API Key", "🤖 Expert Management", "⚠️ Danger Zone", "ℹ️ About"]
    active_tab = st.segmented_control(
        "Settings Sections",
        options=tabs,
        default=tabs[st.session_state.settings_active_tab],
        label_visibility="collapsed",
        key="settings_tabs",
    )

    # Update session state with the current tab
    st.session_state.settings_active_tab = tabs.index(active_tab)

    # Render the appropriate section based on active tab
    if tabs.index(active_tab) == 0:
        render_general_settings_section()
    elif tabs.index(active_tab) == 1:
        render_api_key_section()
    elif tabs.index(active_tab) == 2:
        render_expert_management_section()
    elif tabs.index(active_tab) == 3:
        render_danger_zone_section()
    elif tabs.index(active_tab) == 4:
        render_about_section()

    # Footer
    st.divider()


if __name__ == "__main__":
    main()
