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
from utils.dialogs import create_new_expert, render_add_chat_dialog, render_llm_configuration
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
    """Render the multi-provider API Key management section."""
    st.subheader("🔑 API Key Configuration")

    # Provider selection
    from utils.constants import LLM_PROVIDERS, get_provider_display_name

    # Initialize api_keys in session state if not exists
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

    provider_options = list(LLM_PROVIDERS.keys())
    selected_provider = st.selectbox(
        "Select LLM Provider",
        options=provider_options,
        format_func=lambda x: get_provider_display_name(x),
        key="api_key_provider_selector"
    )

    # Get API keys from session state
    api_keys = st.session_state.api_keys
    current_api_key = api_keys.get(selected_provider, "")

    # Check if key exists in file
    has_file_key = secrets_manager.has_provider_api_key(selected_provider)

    # Current status
    col1, col2 = st.columns(2)

    with col1:
        if has_file_key:
            st.success(f"✅ {get_provider_display_name(selected_provider)} API key saved in secrets.toml")
        else:
            st.info(f"💡 No {get_provider_display_name(selected_provider)} API key in secrets.toml")

    with col2:
        if current_api_key:
            st.success(f"✅ {get_provider_display_name(selected_provider)} API key is available")
        else:
            st.warning(f"⚠️ {get_provider_display_name(selected_provider)} API key not set")

    st.divider()

    # API Key input
    api_key = st.text_input(
        f"{get_provider_display_name(selected_provider)} API Key",
        key=f"settings_api_key_{selected_provider}",
        type="password",
        value="",  # Always show empty for security
        help=f"Enter your {get_provider_display_name(selected_provider)} API key. It will be saved to .streamlit/secrets.toml.",
        placeholder=f"Enter your {get_provider_display_name(selected_provider)} API key here",
    )

    # Save and Clear buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save API Key", type="primary", disabled=not api_key, key=f"save_{selected_provider}"):
            try:
                # Save to secrets.toml file
                secrets_manager.save_provider_api_key(selected_provider, api_key)

                # Update session state
                if "api_keys" not in st.session_state:
                    st.session_state.api_keys = {}
                st.session_state.api_keys[selected_provider] = api_key

                st.success(f"✅ {get_provider_display_name(selected_provider)} API key saved successfully!")
                st.info("🔄 The application will now rerun to load the new key.")

                # Rerun to load the new key from st.secrets
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving API key: {str(e)}")

    with col2:
        if st.button("🗑️ Clear API Key", disabled=not has_file_key, key=f"clear_{selected_provider}"):
            try:
                # Save empty key to remove it from file
                secrets_manager.save_provider_api_key(selected_provider, "")

                # Clear from session state
                if selected_provider in st.session_state.api_keys:
                    del st.session_state.api_keys[selected_provider]

                st.success(f"✅ {get_provider_display_name(selected_provider)} API key cleared successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error clearing API key: {str(e)}")

    st.divider()

    # Resources links
    st.subheader("📚 Resources")

    from utils.constants import get_provider_display_name

    # Provider name and links (one-liner)
    provider_name = get_provider_display_name(selected_provider)

    if selected_provider == "deepseek":
        st.markdown(f"**{provider_name}:** [Chat](https://chat.deepseek.com/) | [Platform](https://platform.deepseek.com/usage)")
    elif selected_provider == "openai":
        st.markdown(f"**{provider_name}:** [Chat](https://chatgpt.com/) | [Platform](https://platform.openai.com/usage)")
    elif selected_provider == "zai":
        st.markdown(f"**{provider_name}:** [Chat](https://chat.z.ai/) | [Platform](https://z.ai/manage-apikey/subscription)")


def render_default_llm_settings_section():
    """Render the Default LLM Settings section for configuring global defaults."""
    st.subheader("⚙️ Default LLM Settings")

    st.caption("These defaults will be used when creating new experts. You can still customize each expert individually.")

    from utils.constants import LLM_PROVIDERS, get_provider_display_name, get_model_display_name, get_default_model_for_provider

    st.divider()

    # Get available providers (only those with API keys configured)
    api_keys = st.session_state.get("api_keys", {})
    available_providers = [p for p in LLM_PROVIDERS.keys() if api_keys.get(p)]

    # Show message if no API keys are configured
    if not available_providers:
        st.warning("⚠️ No API keys configured. Please add API keys in the API Key tab first.")
        return

    # Check if defaults have been explicitly set by user
    defaults_set = (
        st.session_state.get("default_provider") and
        st.session_state.get("default_provider") in available_providers
    )

    if not defaults_set:
        st.info("👋 Welcome! Please configure your default LLM settings below. These will be used when creating new experts.")

    # Default provider selection (filtered to available providers only)
    current_default_provider = st.session_state.get("default_provider")

    # Only auto-select if no provider is set, otherwise use existing value
    if not current_default_provider or current_default_provider not in available_providers:
        current_default_provider = None

    provider_index = available_providers.index(current_default_provider) if current_default_provider in available_providers else 0

    default_provider = st.selectbox(
        "Default Provider",
        options=available_providers,
        index=provider_index,
        format_func=lambda x: get_provider_display_name(x),
        help="The default LLM provider for new experts",
        key="default_provider_selector"
    )

    # Update session state when provider changes
    if st.session_state.get("default_provider") != default_provider:
        st.session_state.default_provider = default_provider
        # Clear the model when provider changes (force user to select)
        if st.session_state.get("default_model"):
            model_for_new_provider = get_default_model_for_provider(default_provider)
            st.session_state.default_model = model_for_new_provider

    # Default model selection (filtered by provider)
    model_options = list(LLM_PROVIDERS[default_provider]["models"].keys())
    current_default_model = st.session_state.get("default_model")

    # Only show default model if it exists for this provider
    if current_default_model not in model_options:
        current_default_model = None

    model_index = model_options.index(current_default_model) if current_default_model in model_options else 0

    default_model = st.selectbox(
        "Default Model",
        options=model_options,
        index=model_index,
        format_func=lambda x: get_model_display_name(default_provider, x),
        help=f"The default {get_provider_display_name(default_provider)} model for new experts",
        key="default_model_selector"
    )

    # Update session state when model changes
    if st.session_state.get("default_model") != default_model:
        st.session_state.default_model = default_model

    # Default thinking mode - show different UI based on provider
    if default_provider == "openai":
        # Show selectbox for OpenAI (use half width like temperature)
        col1, col2 = st.columns(2)
        with col1:
            effort_options = ["none", "low", "medium", "high", "xhigh"]
            current_thinking = st.session_state.get("default_thinking_level", "none")
            effort_index = effort_options.index(current_thinking) if current_thinking in effort_options else 0
            default_thinking_level = st.selectbox(
                "🧠 Select Thinking Mode Level",
                options=effort_options,
                index=effort_index,
                help="Default reasoning effort level for new OpenAI experts",
                key="default_thinking_selector"
            )
    elif default_provider == "zai":
        # Show selectbox for Z.AI (optional thinking mode)
        col1, col2 = st.columns(2)
        with col1:
            thinking_options = ["Disabled", "Enabled"]
            # Map current_thinking to index ("none" -> 0, "medium" -> 1)
            current_thinking = st.session_state.get("default_thinking_level", "none")
            option_index = 1 if current_thinking and current_thinking != "none" else 0
            selected_option = st.selectbox(
                "🧠 Thinking Mode",
                options=thinking_options,
                index=option_index,
                help="New experts will have thinking mode enabled by default",
                key="default_thinking_selector"
            )
            # Convert back to string ("Disabled" -> "none", "Enabled" -> "medium")
            default_thinking_level = "medium" if selected_option == "Enabled" else "none"
    else:
        # DeepSeek: Thinking mode depends on model (no default setting needed)
        # deepseek-chat: no thinking support
        # deepseek-reasoner: thinking always enabled
        default_thinking_level = "none"

    # Save defaults button
    if st.button("💾 Save Defaults", type="primary", key="save_defaults"):
        st.session_state.default_provider = default_provider
        st.session_state.default_model = default_model
        st.session_state.default_thinking_level = default_thinking_level

        st.success(f"✅ Defaults saved! New experts will use {get_provider_display_name(default_provider)} - {get_model_display_name(default_provider, default_model)}")
        st.rerun()

    # Show current settings info
    st.divider()

    # Format thinking level for display
    if st.session_state.default_provider == "openai" and st.session_state.default_thinking_level != "none":
        thinking_display = f"Reasoning ({st.session_state.default_thinking_level})"
    elif st.session_state.default_provider == "deepseek":
        thinking_display = "Determined by model"
    elif st.session_state.default_thinking_level == "none":
        thinking_display = "Disabled"
    else:
        thinking_display = st.session_state.default_thinking_level.capitalize()

    st.info(f"""
    **Current Defaults:**
    - Provider: {get_provider_display_name(st.session_state.default_provider)}
    - Model: {get_model_display_name(st.session_state.default_provider, st.session_state.default_model)}
    - Thinking Mode: {thinking_display}
    """)


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

    # LLM Configuration (Provider, Model, Temperature, Thinking)
    metadata = expert_config.get("metadata", {})
    current_provider = metadata.get("provider", "deepseek")
    current_model = metadata.get("model", "deepseek-chat")
    current_thinking = metadata.get("thinking_level", "none")
    current_temperature = expert_config.get('temperature', 1.0)

    provider, model, temperature, thinking_level = render_llm_configuration(
        current_provider=current_provider,
        current_model=current_model,
        current_temperature=current_temperature,
        current_thinking=current_thinking,
        show_thinking=True
    )

    st.divider()

    with st.form("edit_expert_form"):
        st.subheader("Expert Configuration")

        # Expert ID (read-only)
        st.text_input(
            "Expert ID",
            value=expert_config['expert_id'],
            disabled=True,
            help="Expert ID cannot be changed",
        )

        st.divider()

        # Expert Name
        chat_name = st.text_input(
            "Expert Name *",
            value=expert_config['expert_name'],
            help="A descriptive name for the domain expert",
            max_chars=100,
        ).strip()

        # Add caption with allowed characters
        st.caption("💡 **Allowed characters:** Letters, numbers, spaces, underscores (_), hyphens (-), and dots (.)")

        # Agent Description
        description = st.text_area(
            "Agent Description *",
            value=expert_config['description'],
            help="Detailed description of what this expert specializes in",
            height="content",
            max_chars=1000,
        ).strip()

        st.divider()

        # Get provider from expert config
        metadata = expert_config.get("metadata", {})
        expert_provider = metadata.get("provider", "deepseek")  # Backward compatible

        # Expert Behavior (Advanced) - The most important field!
        st.markdown("### 🧠 Expert Behavior (Advanced)")

        # Check if API key available for this expert's provider
        api_keys = st.session_state.get("api_keys", {})
        api_key_available = bool(api_keys.get(expert_provider, ""))

        if api_key_available:
            caption_text = (
                "💡 **AI-powered generation!** Leave empty to regenerate a customized "
                "system prompt using AI. Provide your own for complete control."
            )
        else:
            caption_text = (
                "💡 **Manual mode**: API key not set, so AI generation is unavailable. "
                "Keep the existing behavior, or provide your own."
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

        # Form buttons (left-aligned)
        st.write("")  # Spacing
        col1, col2, col3 = st.columns([1, 1, 6])

        with col1:
            submit_button = st.form_submit_button("Save Changes", type="primary")

        with col2:
            cancel_button = st.form_submit_button("Cancel")

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

                # Get API key for AI generation (provider-specific)
                api_key = api_keys.get(expert_provider, None) if api_key_available else None

                # Update the config
                config_manager.update_config(
                    editing_expert_id,
                    {
                        "expert_name": chat_name,
                        "description": description,
                        "temperature": temperature,
                        "system_prompt": final_system_prompt,
                        "api_key": api_key,
                        "provider": provider,
                        "model": model,
                        "thinking_level": thinking_level,
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

    # Check if ANY provider API key is available
    api_keys = st.session_state.get("api_keys", {})
    api_key_available = any(api_keys.values())

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
        # Get provider and model info
        metadata = expert.get('metadata', {})
        provider = metadata.get('provider', 'deepseek')
        model = metadata.get('model', 'deepseek-chat')
        thinking_level = metadata.get('thinking_level', 'none')

        # Import for display helpers
        from utils.constants import get_provider_display_name, get_model_display_name

        provider_name = get_provider_display_name(provider)
        model_name = get_model_display_name(provider, model)

        with st.expander(f"📝 {expert['expert_name']}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                # Show provider/model info
                st.markdown(
                    f"**LLM:** {provider_name} - {model_name}"
                )
                # Show thinking mode status
                if provider == "openai" and thinking_level != "none":
                    st.caption(f"🧠 Reasoning Effort: {thinking_level.capitalize()}")
                elif thinking_level != "none":
                    st.caption("🧠 Thinking Mode: Enabled")
                st.markdown(f"**Temperature:** `{expert['temperature']}`")
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
    """)
    st.markdown("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/fossler/expertgpts)")


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
    tabs = ["🎨 General", "🔑 API Key", "⚙️ Default LLM", "🤖 Expert Management", "⚠️ Danger Zone", "ℹ️ About"]
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
        render_default_llm_settings_section()
    elif tabs.index(active_tab) == 3:
        render_expert_management_section()
    elif tabs.index(active_tab) == 4:
        render_danger_zone_section()
    elif tabs.index(active_tab) == 5:
        render_about_section()

    # Footer
    st.divider()


if __name__ == "__main__":
    main()
