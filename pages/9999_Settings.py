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
from utils.constants import EXPERT_BEHAVIOR_DOCS, get_expert_behavior_docs_edit
from utils.dialogs import create_new_expert, render_add_chat_dialog, render_llm_configuration
from utils.helpers import sanitize_name, translate_expert_name
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
    from utils.i18n import i18n
    from utils.constants import LLM_PROVIDERS, get_provider_display_name

    st.subheader(f"🔑 {i18n.t('api_key.title')}")

    # Provider selection

    # Initialize api_keys in session state if not exists
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

    provider_options = list(LLM_PROVIDERS.keys())
    selected_provider = st.selectbox(
        i18n.t('api_key.select_provider'),
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
            st.success(f"✅ {i18n.t('status.api_key_saved_in_secrets', provider=get_provider_display_name(selected_provider))}")
        else:
            st.info(f"💡 {i18n.t('status.no_api_key_in_secrets', provider=get_provider_display_name(selected_provider))}")

    with col2:
        if current_api_key:
            st.success(f"✅ {i18n.t('status.api_key_available', provider=get_provider_display_name(selected_provider))}")
        else:
            st.warning(f"⚠️ {i18n.t('status.api_key_not_set_warning', provider=get_provider_display_name(selected_provider))}")

    st.divider()

    # API Key input
    api_key = st.text_input(
        i18n.t('forms.api_key'),
        key=f"settings_api_key_{selected_provider}",
        type="password",
        value="",  # Always show empty for security
        help=i18n.t('api_key.enter_key_help', provider=get_provider_display_name(selected_provider)),
        placeholder=i18n.t('api_key.enter_key', provider=get_provider_display_name(selected_provider)),
    )

    # Save and Clear buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"💾 {i18n.t('buttons.save_api_key')}", type="primary", disabled=not api_key, key=f"save_{selected_provider}"):
            try:
                # Save to secrets.toml file
                secrets_manager.save_provider_api_key(selected_provider, api_key)

                # Update session state
                if "api_keys" not in st.session_state:
                    st.session_state.api_keys = {}
                st.session_state.api_keys[selected_provider] = api_key

                st.success(f"✅ {i18n.t('success.api_key_saved')}")
                st.info(f"🔄 {i18n.t('status.application_will_rerun')}")

                # Rerun to load the new key from st.secrets
                st.rerun()
            except Exception as e:
                st.error(f"❌ {i18n.t('errors.error_saving_api_key', error=str(e))}")

    with col2:
        if st.button(f"🗑️ {i18n.t('buttons.clear')}", disabled=not has_file_key, key=f"clear_{selected_provider}"):
            try:
                # Save empty key to remove it from file
                secrets_manager.save_provider_api_key(selected_provider, "")

                # Clear from session state
                if selected_provider in st.session_state.api_keys:
                    del st.session_state.api_keys[selected_provider]

                st.success(f"✅ {i18n.t('success.api_key_cleared', provider=get_provider_display_name(selected_provider))}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {i18n.t('errors.error_clearing_api_key', error=str(e))}")

    st.divider()

    # Resources links
    st.subheader(f"📚 {i18n.t('api_key.resources')}")

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
    from utils.i18n import i18n
    from utils.constants import LLM_PROVIDERS, get_provider_display_name, get_model_display_name, get_default_model_for_provider

    st.subheader(f"⚙️ {i18n.t('default_llm.title')}")

    st.caption(i18n.t('default_llm.description'))

    st.divider()

    # Get available providers (only those with API keys configured)
    api_keys = st.session_state.get("api_keys", {})
    available_providers = [p for p in LLM_PROVIDERS.keys() if api_keys.get(p)]

    # Show message if no API keys are configured
    if not available_providers:
        st.warning(f"⚠️ {i18n.t('api_key.no_api_keys_configured')}")
        return

    # Default provider selection (filtered to available providers only)
    current_default_provider = st.session_state.get("default_provider")

    # If current default provider is not available or not set, use first available
    if not current_default_provider or current_default_provider not in available_providers:
        current_default_provider = available_providers[0]

    provider_index = available_providers.index(current_default_provider)

    default_provider = st.selectbox(
        i18n.t('default_llm.default_provider'),
        options=available_providers,
        index=provider_index,
        format_func=lambda x: get_provider_display_name(x),
        help=i18n.t('default_llm.default_provider_help'),
        key="default_provider_selector"
    )

    # Update session state when provider changes
    if st.session_state.get("default_provider") != default_provider:
        st.session_state.default_provider = default_provider
        # Update model to match new provider
        new_model = get_default_model_for_provider(default_provider)
        st.session_state.default_model = new_model

    # Default model selection (filtered by provider)
    model_options = list(LLM_PROVIDERS[default_provider]["models"].keys())
    current_default_model = st.session_state.get("default_model")

    # If current default model is not in the new provider's models, use provider default
    if not current_default_model or current_default_model not in model_options:
        current_default_model = get_default_model_for_provider(default_provider)
        st.session_state.default_model = current_default_model

    model_index = model_options.index(current_default_model) if current_default_model in model_options else 0

    default_model = st.selectbox(
        i18n.t('default_llm.default_model'),
        options=model_options,
        index=model_index,
        format_func=lambda x: get_model_display_name(default_provider, x),
        help=i18n.t('default_llm.default_model_help', provider=get_provider_display_name(default_provider)),
        key="default_model_selector"
    )

    # Update session state when model changes
    if st.session_state.get("default_model") != default_model:
        st.session_state.default_model = default_model

    # Default thinking mode - show different UI based on provider
    current_thinking = st.session_state.get("default_thinking_level", "none")

    if default_provider == "openai":
        # Show selectbox for OpenAI (use half width like temperature)
        col1, col2 = st.columns(2)
        with col1:
            effort_options = ["none", "low", "medium", "high", "xhigh"]
            effort_index = effort_options.index(current_thinking) if current_thinking in effort_options else 0
            default_thinking_level = st.selectbox(
                f"🧠 {i18n.t('default_llm.select_thinking_mode')}",
                options=effort_options,
                index=effort_index,
                help=i18n.t('default_llm.thinking_mode_help'),
                key="default_thinking_selector"
            )
    elif default_provider == "zai":
        # Show selectbox for Z.AI (optional thinking mode)
        col1, col2 = st.columns(2)
        with col1:
            thinking_options = [i18n.t('sidebar.disabled'), i18n.t('sidebar.enabled')]
            # Map current_thinking to index ("none" -> 0, "medium" -> 1)
            option_index = 1 if current_thinking and current_thinking != "none" else 0
            selected_option = st.selectbox(
                f"🧠 {i18n.t('default_llm.thinking_mode')}",
                options=thinking_options,
                index=option_index,
                help=i18n.t('default_llm.thinking_mode_help_zai'),
                key="default_thinking_selector"
            )
            # Convert back to string ("Disabled" -> "none", "Enabled" -> "medium")
            default_thinking_level = "medium" if selected_option == i18n.t('sidebar.enabled') else "none"
    else:
        # DeepSeek: Thinking mode depends on model (no default setting needed)
        # deepseek-chat: no thinking support
        # deepseek-reasoner: thinking always enabled
        default_thinking_level = "none"

    # Save defaults button
    if st.button(f"💾 {i18n.t('buttons.save_defaults')}", type="primary", key="save_defaults"):
        st.session_state.default_provider = default_provider
        st.session_state.default_model = default_model
        st.session_state.default_thinking_level = default_thinking_level

        st.success(f"✅ {i18n.t('success.defaults_saved', provider=get_provider_display_name(default_provider), model=get_model_display_name(default_provider, default_model))}")
        st.rerun()


def render_general_settings_section():
    """Render the General Settings section for theme and language customization."""
    from utils.i18n import i18n

    # Theme Customization
    st.subheader(f"🎨 {i18n.t('theme.title')}")

    st.caption(i18n.t('theme.description'))

    st.divider()

    # Define 7 complete themes with harmonious colors
    # Using theme keys as identifiers, display names will be translated
    themes = {
        "modern_red": {
            "primary": "#FF6B6B",
            "background": "#FFFFFF",
            "secondary": "#F0F2F6",
            "text": "#262730",
            "icon": "🔴"
        },
        "ocean_blue": {
            "primary": "#4A90E2",
            "background": "#FFFFFF",
            "secondary": "#E8F0FE",
            "text": "#1E3A8A",
            "icon": "🔵"
        },
        "forest_green": {
            "primary": "#10B981",
            "background": "#FFFFFF",
            "secondary": "#ECFDF5",
            "text": "#064E3B",
            "icon": "🟢"
        },
        "royal_purple": {
            "primary": "#9B59B6",
            "background": "#FFFFFF",
            "secondary": "#F3E5F5",
            "text": "#4A148C",
            "icon": "🟣"
        },
        "dark_blue": {
            "primary": "#4A90E2",
            "background": "#0E1117",
            "secondary": "#262730",
            "text": "#FAFAFA",
            "icon": "🌑"
        },
        "dark_gray": {
            "primary": "#FF6B6B",
            "background": "#1A1A1A",
            "secondary": "#2D2D2D",
            "text": "#FFFFFF",
            "icon": "🖤"
        },
        "custom": {
            "primary": "#F59E0B",
            "background": "#FFFBEB",
            "secondary": "#FEF3C7",
            "text": "#78350F",
            "icon": "🎨"
        }
    }

    # Create theme options with icons (using translated names)
    theme_options = [f"{theme['icon']} {i18n.t(f'theme.{name}')}" for name, theme in themes.items()]
    theme_labels = {f"{theme['icon']} {i18n.t(f'theme.{name}')}": name for name, theme in themes.items()}

    # Initialize session state for selected theme KEY (language-independent) and colors
    if "selected_theme_key" not in st.session_state:
        # Read current theme from config file (now includes theme_name!)
        current_config = config_toml_manager.get_theme_settings()

        # Get the saved theme name directly (defaults to "custom" if not set)
        saved_theme_name = current_config.get("theme_name", "custom")

        # Validate that the saved theme name exists in our predefined themes
        if saved_theme_name in themes and saved_theme_name != "custom":
            # Use the saved theme directly - no color comparison needed!
            theme_data = themes[saved_theme_name]
            st.session_state.selected_theme_key = saved_theme_name
            st.session_state.theme_primary_color = theme_data["primary"]
            st.session_state.theme_background_color = theme_data["background"]
            st.session_state.theme_secondary_background_color = theme_data["secondary"]
            st.session_state.theme_text_color = theme_data["text"]
        else:
            # Use Custom theme with current config values
            st.session_state.selected_theme_key = "custom"
            st.session_state.theme_primary_color = current_config.get("primaryColor", "#F59E0B")
            st.session_state.theme_background_color = current_config.get("backgroundColor", "#FFFBEB")
            st.session_state.theme_secondary_background_color = current_config.get("secondaryBackgroundColor", "#FEF3C7")
            st.session_state.theme_text_color = current_config.get("textColor", "#78350F")

    # Get the current display name for the selected theme key (in current language)
    current_theme_display = f"{themes[st.session_state.selected_theme_key]['icon']} {i18n.t(f'theme.{st.session_state.selected_theme_key}')}"

    # Radio button for theme selection (outside form for reactivity)
    selected_theme = st.radio(
        i18n.t('theme.select_theme'),
        options=theme_options,
        index=theme_options.index(current_theme_display),
        horizontal=True,
        key="theme_radio_selector"
    )

    # Extract theme name from selected option
    theme_name = theme_labels[selected_theme]
    theme_colors = themes[theme_name]

    # Update session state and rerun if selection changed
    if theme_name != st.session_state.selected_theme_key:
        st.session_state.selected_theme_key = theme_name
        # Update color values in session state
        st.session_state.theme_primary_color = theme_colors["primary"]
        st.session_state.theme_background_color = theme_colors["background"]
        st.session_state.theme_secondary_background_color = theme_colors["secondary"]
        st.session_state.theme_text_color = theme_colors["text"]
        st.rerun()

    st.divider()

    # Color Preview section (outside form for reactivity)
    st.markdown(f"### {i18n.t('forms.color_preview')}")

    # Check if Custom theme is selected
    is_custom_theme = (theme_name == "custom")

    # Create columns for color inputs in one row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        primary_color = st.color_picker(
            i18n.t('forms.buttons_elements'),
            value=st.session_state.theme_primary_color,
            help=i18n.t('theme.buttons_elements_help'),
            key=f"primary_{st.session_state.selected_theme_key}",
            disabled=not is_custom_theme
        )

    with col2:
        background_color = st.color_picker(
            i18n.t('forms.background_color'),
            value=st.session_state.theme_background_color,
            help=i18n.t('theme.background_help'),
            key=f"background_{st.session_state.selected_theme_key}",
            disabled=not is_custom_theme
        )

    with col3:
        secondary_background_color = st.color_picker(
            i18n.t('forms.secondary_background'),
            value=st.session_state.theme_secondary_background_color,
            help=i18n.t('theme.secondary_background_help'),
            key=f"secondary_{st.session_state.selected_theme_key}",
            disabled=not is_custom_theme
        )

    with col4:
        text_color = st.color_picker(
            i18n.t('forms.text_color'),
            value=st.session_state.theme_text_color,
            help=i18n.t('theme.text_help'),
            key=f"text_{st.session_state.selected_theme_key}",
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
            primary_key = f"primary_{st.session_state.selected_theme_key}"
            background_key = f"background_{st.session_state.selected_theme_key}"
            secondary_key = f"secondary_{st.session_state.selected_theme_key}"
            text_key = f"text_{st.session_state.selected_theme_key}"

            # Get the current theme name directly from session state
            current_theme_name = st.session_state.selected_theme_key

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
            st.toast(f"✅ {i18n.t('status.theme_saved_reloading')}", icon="🎨")
        except Exception as e:
            st.error(f"❌ {i18n.t('errors.error', error=str(e))}")

    with col1:
        if st.button(f"💾 {i18n.t('buttons.save_apply_theme')}", key="save_apply_button", on_click=save_and_apply_theme, type="primary"):
            pass

    with col2:
        st.empty()  # Spacer

    with col3:
        st.empty()  # Spacer

    st.divider()

    # Language selector
    st.subheader(f"🌐 {i18n.t('language.title')}")

    # Get current language
    current_lang = st.session_state.get("language", "en")
    current_info = i18n.get_language_info(current_lang)

    # Display current language
    st.caption(f"{i18n.t('language.current_language')}: {current_info['flag']} {current_info['native_name']}")

    st.divider()

    # Group languages by script for better UX
    latin_langs = ["en", "de", "fr", "es", "it", "pt", "tr", "id", "ms"]
    cyrillic_langs = ["ru"]
    han_langs = ["zh-CN", "zh-TW", "wyw", "yue"]

    # Latin Script Languages
    st.write(f"**{i18n.t('language.latin_script')}**")
    cols_latin = st.columns(3)
    for idx, code in enumerate(latin_langs):
        info = i18n.get_language_info(code)
        with cols_latin[idx % 3]:
            if st.button(
                f"{info['flag']} {info['native_name']}",
                key=f"lang_{code}",
                use_container_width=True,
                type="secondary" if code != current_lang else "primary"
            ):
                i18n.set_language(code)

    # Cyrillic Script Languages
    st.write(f"**{i18n.t('language.cyrillic_script')}**")
    cols_cyrillic = st.columns(3)
    for idx, code in enumerate(cyrillic_langs):
        info = i18n.get_language_info(code)
        with cols_cyrillic[idx]:
            if st.button(
                f"{info['flag']} {info['native_name']}",
                key=f"lang_{code}",
                use_container_width=True,
                type="secondary" if code != current_lang else "primary"
            ):
                i18n.set_language(code)

    # Chinese (Han Script) Languages
    st.write(f"**{i18n.t('language.han_script')}**")
    cols_han = st.columns(2)
    for idx, code in enumerate(han_langs):
        info = i18n.get_language_info(code)
        with cols_han[idx % 2]:
            if st.button(
                f"{info['flag']} {info['native_name']}",
                key=f"lang_{code}",
                use_container_width=True,
                type="secondary" if code != current_lang else "primary"
            ):
                i18n.set_language(code)


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
    from utils.i18n import i18n
    config_manager = ConfigManager()
    try:
        expert_config = config_manager.load_config(editing_expert_id)
    except FileNotFoundError:
        st.error(f"❌ {i18n.t('errors.expert_not_found', expert_id=editing_expert_id)}")
        # Clear the editing state
        for key in st.session_state:
            if key.startswith("editing_expert_"):
                st.session_state[key] = False
        st.rerun()
        return

    # Translate expert name for title
    translated_name = translate_expert_name(expert_config['expert_name'])
    st.title(f"✏️ Edit Expert: {translated_name}")

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
        st.subheader(i18n.t('dialogs.add_chat.expert_configuration'))

        # Expert ID (read-only)
        st.text_input(
            i18n.t('forms.expert_id'),
            value=expert_config['expert_id'],
            disabled=True,
            help=i18n.t('dialogs.edit_expert.expert_id_help'),
        )

        st.divider()

        # Expert Name
        chat_name = st.text_input(
            f"{i18n.t('forms.expert_name')} *",
            value=expert_config['expert_name'],
            help=i18n.t('dialogs.add_chat.help_expert_name'),
            max_chars=100,
        ).strip()

        # Add caption with allowed characters
        st.caption(f"💡 **{i18n.t('forms.allowed_characters')}:** {i18n.t('forms.allowed_characters_desc')}")

        # Agent Description
        description = st.text_area(
            f"{i18n.t('forms.agent_description')} *",
            value=expert_config['description'],
            help=i18n.t('dialogs.add_chat.help_expert_description'),
            height="content",
            max_chars=1000,
        ).strip()

        st.divider()

        # Get provider from expert config
        metadata = expert_config.get("metadata", {})
        expert_provider = metadata.get("provider", "deepseek")  # Backward compatible

        # Expert Behavior (Advanced) - The most important field!
        st.markdown(f"### 🧠 {i18n.t('dialogs.add_chat.expert_behavior_title')}")

        # Check if API key available for this expert's provider
        api_keys = st.session_state.get("api_keys", {})
        api_key_available = bool(api_keys.get(expert_provider, ""))

        if api_key_available:
            caption_text = (
                f"💡 {i18n.t('dialogs.edit_expert.ai_powered_regeneration')}"
            )
        else:
            caption_text = (
                f"💡 {i18n.t('dialogs.edit_expert.manual_mode_regeneration')}"
            )

        st.caption(caption_text)

        custom_system_prompt = st.text_area(
            i18n.t('forms.custom_system_prompt'),
            value=expert_config.get('system_prompt', ''),
            height=250,
            help=i18n.t('dialogs.add_chat.help_custom_behavior'),
            max_chars=3000,
        ).strip()

        # Inform users about automatic language response
        st.caption(f"💡 {i18n.t('info.language_prefix_auto')}")

        # Add expander with examples
        with st.expander(f"📖 {i18n.t('dialogs.add_chat.why_important_title')}"):
            st.markdown(get_expert_behavior_docs_edit())

        st.caption(i18n.t('info.required_fields_hint'))

        # Form buttons (left-aligned)
        st.write("")  # Spacing
        col1, col2, col3 = st.columns([1, 1, 6])

        with col1:
            submit_button = st.form_submit_button(i18n.t('buttons.save_changes'), type="primary")

        with col2:
            cancel_button = st.form_submit_button(i18n.t('buttons.cancel'))

        # Handle form submission
        if submit_button:
            if not chat_name or not description:
                st.error(i18n.t('errors.required_fields'))
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

                st.success(f"✅ {i18n.t('status.expert_updated', name=chat_name)}")
                st.info(f"🔄 {i18n.t('status.refreshing')}")

                st.rerun()

            except Exception as e:
                st.error(f"❌ {i18n.t('errors.error_updating_expert', error=str(e))}")

        if cancel_button:
            # Clear the editing state
            st.session_state[f"editing_expert_{editing_expert_id}"] = False
            st.rerun()


def render_expert_management_section():
    """Render the Expert Management section."""
    from utils.i18n import i18n

    st.subheader(f"🤖 {i18n.t('experts.management.title')}")

    # Check if ANY provider API key is available
    api_keys = st.session_state.get("api_keys", {})
    api_key_available = any(api_keys.values())

    if api_key_available:
        if st.button(f"➕ {i18n.t('buttons.add_new_chat')}", type="primary", width="content"):
            st.session_state.show_add_chat_dialog = True
            st.rerun()
    else:
        st.button(
            f"➕ {i18n.t('buttons.add_new_chat')}",
            type="primary",
            width="content",
            disabled=True,
            help=i18n.t('info.set_api_key_to_create')
        )
        st.caption(f"⚠️ {i18n.t('info.set_api_key_to_create')}")

    st.divider()

    # Load experts (not cached to avoid tab switching issues)
    config_manager = ConfigManager()
    experts = config_manager.list_experts()

    if not experts:
        st.info(f"🔍 {i18n.t('info.create_first_expert')}")
        return

    st.caption(i18n.t('status.found_experts', count=len(experts)))

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

        # Translate expert name for display
        translated_name = translate_expert_name(expert['expert_name'])

        with st.expander(f"📝 {translated_name}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                # Show provider/model info
                st.markdown(
                    f"**LLM:** {provider_name} - {model_name}"
                )
                # Show thinking mode status
                if provider == "openai" and thinking_level != "none":
                    st.caption(f"🧠 {i18n.t('experts.management.reasoning_effort', level=thinking_level.capitalize())}")
                elif thinking_level != "none":
                    st.caption(f"🧠 {i18n.t('experts.management.thinking_mode_enabled')}")
                st.markdown(f"**Temperature:** `{expert['temperature']}`")
                st.markdown(f"**{i18n.t('experts.management.description_label')}:**")
                st.text_area(
                    i18n.t('experts.management.description_label'),
                    value=expert['description'],
                    height=None,
                    disabled=True,
                    key=f"desc_preview_{expert['expert_id']}",
                    label_visibility="collapsed",
                )

                # Show expert behavior
                system_prompt = expert.get('system_prompt', '')
                if system_prompt:
                    st.markdown(f"**🧠 {i18n.t('experts.management.expert_behavior')}:**")
                    # Show language prefix that will be automatically added
                    language_prefix = i18n.get_language_prefix()
                    st.caption(f"💡 **{language_prefix}**")
                    # Display as read-only text area preview
                    st.text_area(
                        i18n.t('experts.management.expert_behavior'),
                        value=system_prompt,
                        height=None,
                        disabled=True,
                        key=f"preview_{expert['expert_id']}",
                        label_visibility="collapsed",
                    )
                else:
                    st.markdown(f"**🧠 {i18n.t('experts.management.expert_behavior')}:** {i18n.t('info.expert_behavior_auto')}")
                    # Show language prefix that will be automatically added
                    language_prefix = i18n.get_language_prefix()
                    st.caption(f"💡 **{language_prefix}**")

            with col2:
                st.markdown(f"**{i18n.t('experts.management.actions')}**")
                edit_key = f"edit_{expert['expert_id']}"
                if st.button(f"✏️ {i18n.t('buttons.edit')}", key=edit_key, width="stretch"):
                    st.session_state[f"editing_expert_{expert['expert_id']}"] = True
                    st.rerun()

                delete_key = f"delete_{expert['expert_id']}"
                if st.button(f"🗑️ {i18n.t('buttons.delete')}", key=delete_key, width="stretch"):
                    st.session_state[f"confirm_delete_{expert['expert_id']}"] = True

        # Confirmation dialog for deletion
        if st.session_state.get(f"confirm_delete_{expert['expert_id']}"):
            translated_name = translate_expert_name(expert['expert_name'])
            st.warning(f"⚠️ {i18n.t('experts.management.confirm_delete', name=translated_name)}")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"✅ {i18n.t('buttons.yes_delete')}", key=f"confirm_{expert['expert_id']}", type="primary"):
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

                        # Get translated name for success message
                        translated_name = translate_expert_name(expert['expert_name'])
                        st.success(f"✅ {i18n.t('success.expert_deleted', name=translated_name)}")
                        st.session_state[f"confirm_delete_{expert['expert_id']}"] = False
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ {i18n.t('errors.error_deleting_expert', error=str(e))}")

            with col2:
                if st.button(f"❌ {i18n.t('buttons.cancel')}", key=f"cancel_{expert['expert_id']}"):
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
    from utils.i18n import i18n

    st.subheader(f"⚠️ {i18n.t('danger_zone.title')}")

    st.warning(f"⚠️ **{i18n.t('danger_zone.warning')}**")

    # Download configs section
    st.markdown("---")
    st.markdown(f"### 💾 {i18n.t('danger_zone.backup_title')}")

    st.markdown(i18n.t('danger_zone.backup_description'))

    # Get the zip file content
    config_zip = get_configs_as_zip()

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"expertgpts_configs_{timestamp}.zip"

    # Download button
    st.download_button(
        label=f"📥 {i18n.t('danger_zone.download_button')}",
        data=config_zip,
        file_name=filename,
        mime="application/zip",
        width="content",
    )

    st.markdown("---")

    st.markdown(i18n.t('danger_zone.reset_description'))

    if st.button(f"🔄 {i18n.t('danger_zone.reset_button')}", type="primary", width="content"):
        st.session_state.confirm_reset = True

    if st.session_state.get("confirm_reset"):
        st.error(f"🚨 **{i18n.t('danger_zone.final_warning')}**")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(f"✅ {i18n.t('buttons.yes_reset_everything')}", key="confirm_reset_button", type="primary"):
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
                    st.info(f"🔄 {i18n.t('status.recreating_experts')}")

                    # Run scripts/setup.py as a subprocess
                    result = subprocess.run(
                        [sys.executable, "scripts/setup.py"],
                        check=True,
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent.parent
                    )

                    st.success(f"✅ {i18n.t('success.application_reset')}")
                    st.info(f"🔄 {i18n.t('status.restarting_application')}")

                    st.session_state.confirm_reset = False
                    st.rerun()

                except subprocess.CalledProcessError as e:
                    st.error(f"❌ {i18n.t('errors.error_recreating_experts', error=str(e))}")
                    if e.stdout:
                        st.error(f"Output: {e.stdout}")
                    if e.stderr:
                        st.error(f"Error: {e.stderr}")
                except Exception as e:
                    st.error(f"❌ {i18n.t('errors.error_resetting_application', error=str(e))}")

        with col2:
            if st.button(f"❌ {i18n.t('buttons.cancel')}", key="cancel_reset_button"):
                st.session_state.confirm_reset = False
                st.rerun()


def render_about_section():
    """Render the About section."""
    from utils.i18n import i18n

    st.subheader(f"ℹ️ {i18n.t('about.title')}")

    st.markdown(f"""
    ### ExpertGPTs

    {i18n.t('about.description')}

    **{i18n.t('about.version')}**

    **{i18n.t('about.features_title')}:**
    - 🎯 {i18n.t('about.feature_domain_experts')}
    - 🔧 {i18n.t('about.feature_customizable')}
    - 🌡️ {i18n.t('about.feature_temperature')}
    - 💾 {i18n.t('about.feature_chat_history')}
    - 📋 {i18n.t('about.feature_template_generation')}

    ### {i18n.t('about.development')}
    """)

    # Display z.ai icon and link
    col1, col2 = st.columns([1, 6])
    with col1:
        # Read the SVG file and embed as data URL
        import base64
        from pathlib import Path

        icon_path = Path("icons/zai_logo.svg")
        if icon_path.exists():
            with open(icon_path, "rb") as f:
                svg_data = f.read().decode("utf-8")
            # Encode SVG as base64 data URL
            svg_base64 = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")
            data_url = f"data:image/svg+xml;base64,{svg_base64}"

            # Make the icon clickable
            st.markdown(
                f'<a href="https://z.ai/subscribe?ic=JGTYCX7ZO7" target="_blank">'
                f'<img src="{data_url}" width="100"></a>',
                unsafe_allow_html=True
            )
        else:
            # Fallback to non-clickable image if file not found
            st.image("icons/zai_logo.svg", width=100)

        st.markdown(i18n.t('about.developed_with'))
    with col2:
        st.empty()

    st.markdown(f"""
    ### {i18n.t('about.resources')}
    """)
    st.markdown("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/fossler/expertgpts)")

    st.markdown(f"""
    ### {i18n.t('about.support')}
    """)

    # Buy Me a Coffee button
    st.markdown(
        '<a href="https://www.buymeacoffee.com/MirzetKadic" target="_blank">'
        '<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" '
        'alt="Buy Me A Coffee" '
        'style="height: 60px !important; width: 217px !important; border-radius: 5px;"></a>',
        unsafe_allow_html=True
    )


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

    from utils.i18n import i18n

    st.title(f"⚙️ {i18n.t('settings.title')}")

    # Tab-based navigation for different settings sections (stateful)
    tabs = [
        f"🎨 {i18n.t('settings.sections.general')}",
        f"🔑 {i18n.t('settings.sections.api_key')}",
        f"⚙️ {i18n.t('settings.sections.default_llm')}",
        f"🤖 {i18n.t('settings.sections.expert_management')}",
        f"⚠️ {i18n.t('settings.sections.danger_zone')}",
        f"ℹ️ {i18n.t('settings.sections.about')}"
    ]
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
