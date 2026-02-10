"""Shared dialog rendering functions for ExpertGPTs application.

This module contains reusable dialog components to avoid code duplication
across multiple pages.
"""

import streamlit as st
from pathlib import Path
from lib.config.config_manager import ConfigManager
from lib.shared.constants import get_expert_behavior_docs, LLM_PROVIDERS, get_provider_display_name, get_model_display_name, get_default_model_for_provider
from lib.config.app_defaults_manager import get_llm_defaults
from lib.shared.page_generator import PageGenerator
from lib.shared.helpers import sanitize_name, validate_expert_name
from lib.i18n.i18n import i18n


def render_thinking_mode_ui(
    provider: str,
    current_thinking: str,
    widget_key: str,
    label: str = None,
    help_text: str = None,
    use_sidebar: bool = False
) -> str:
    """Render thinking mode UI based on provider.

    This helper function centralizes thinking mode rendering logic,
    eliminating duplication across template.py, Settings.py, and dialogs.py.

    Args:
        provider: LLM provider (openai, zai, deepseek)
        current_thinking: Current thinking level
        widget_key: Unique key for the widget
        label: Optional label (auto-generated if None)
        help_text: Optional help text
        use_sidebar: If True, use st.sidebar instead of st

    Returns:
        str: The thinking level value
    """
    st_func = st.sidebar if use_sidebar else st

    if provider == "openai":
        effort_options = ["none", "low", "medium", "high", "xhigh"]
        effort_index = effort_options.index(current_thinking) if current_thinking in effort_options else 0
        thinking_level = st_func.selectbox(
            label or i18n.t("sidebar.thinking_mode"),
            options=effort_options,
            index=effort_index,
            format_func=lambda x: x.capitalize(),
            help=help_text,
            key=widget_key
        )
        return thinking_level
    elif provider == "zai":
        thinking_options = [i18n.t("sidebar.disabled"), i18n.t("sidebar.enabled")]
        option_index = 1 if current_thinking and current_thinking != "none" else 0
        selected_option = st_func.selectbox(
            label or i18n.t("sidebar.thinking_mode"),
            options=thinking_options,
            index=option_index,
            help=help_text,
            key=widget_key
        )
        return "medium" if selected_option == i18n.t("sidebar.enabled") else "none"
    else:
        # DeepSeek or other providers: no thinking mode control
        return current_thinking or "none"


def render_model_selection(
    provider: str,
    current_model: str,
    widget_key: str,
    label: str = None,
    help_text: str = None,
    use_sidebar: bool = False,
    update_session_state: bool = False,
    session_state_key: str = None
) -> str:
    """Render model selection dropdown for a provider.

    This helper function centralizes model selection logic,
    eliminating duplication across Settings.py, template.py, and dialogs.py.

    Args:
        provider: LLM provider
        current_model: Currently selected model
        widget_key: Unique widget key
        label: Optional label (auto-generated if None)
        help_text: Optional help text
        use_sidebar: If True, use st.sidebar
        update_session_state: If True, update session state
        session_state_key: Session state key to update (e.g., "default_model")

    Returns:
        str: Selected model
    """
    st_func = st.sidebar if use_sidebar else st
    model_options = list(LLM_PROVIDERS[provider]["models"].keys())

    # Handle model not in options
    if current_model not in model_options:
        current_model = get_default_model_for_provider(provider)
        if update_session_state and session_state_key:
            st.session_state[session_state_key] = current_model

    model_index = model_options.index(current_model) if current_model in model_options else 0

    selected_model = st_func.selectbox(
        label or i18n.t("sidebar.model"),
        options=model_options,
        index=model_index,
        format_func=lambda x: get_model_display_name(provider, x),
        help=help_text,
        key=widget_key
    )

    if update_session_state and session_state_key:
        st.session_state[session_state_key] = selected_model

    return selected_model


def render_temperature_input(
    value: float = 1.0,
    provider: str = None,
    use_sidebar: bool = False,
    widget_key: str = None,
    show_help: bool = True
) -> float:
    """Render temperature input field.

    Args:
        value: Current temperature value (default: 1.0)
        provider: LLM provider (to disable slider for OpenAI)
        use_sidebar: If True, render in sidebar
        widget_key: Unique widget key
        show_help: If True, show help expander

    Returns:
        float: Temperature value from user input
    """
    st_func = st.sidebar if use_sidebar else st

    # OpenAI models only support temperature=1.0
    if provider == "openai":
        temperature = st_func.number_input(
            i18n.t('forms.temperature'),
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.01,
            help=i18n.t('dialogs.temperature.fixed_for_openai') if show_help else None,
            disabled=True,
            format="%.2f",
            key=widget_key
        )
        if show_help:
            st.caption(f"⚠️ {i18n.t('dialogs.temperature.openai_warning')}")
    else:
        temperature = st_func.number_input(
            i18n.t('forms.temperature'),
            min_value=0.0,
            max_value=2.0,
            value=value,
            step=0.1,
            help=i18n.t('dialogs.temperature.help_creativity') if show_help else None,
            format="%.1f",
            key=widget_key
        )

        # Add expander with detailed temperature guidance (only for non-OpenAI)
        if show_help:
            with (st.sidebar if use_sidebar else st).expander(f"📖 {i18n.t('dialogs.temperature.recommended_values')}", expanded=False):
                st.markdown(f"**{i18n.t('dialogs.temperature.use_case_guidelines')}**\n")
                st.markdown(f"• **0.0** - {i18n.t('dialogs.temperature.coding')}")
                st.markdown(f"• **1.0** - {i18n.t('dialogs.temperature.data_analysis')}")
                st.markdown(f"• **1.3** - {i18n.t('dialogs.temperature.conversation')}")
                st.markdown(f"• **1.5** - {i18n.t('dialogs.temperature.creative_writing')}")
                st.caption(f"\n*{i18n.t('dialogs.temperature.based_on_docs')}*")

    return temperature


def render_llm_configuration(
    current_provider: str = None,
    current_model: str = None,
    current_temperature: float = 1.0,
    current_thinking: str = None,
    show_thinking: bool = True,
    is_defaults: bool = False
) -> tuple:
    """Render complete LLM configuration UI (Provider, Model, Temperature, Thinking).

    This combines provider selection and temperature into one logical unit,
    ensuring temperature UI adapts to provider choice in real-time.

    Args:
        current_provider: Currently selected provider (defaults to session state default)
        current_model: Currently selected model (defaults to provider default)
        current_temperature: Current temperature value (default: 1.0)
        current_thinking: Current thinking/reasoning level (OpenAI: "none"|"low"|"medium"|"high"|"xhigh")
        show_thinking: Whether to show thinking UI element
        is_defaults: Whether this is for default settings (affects labels and keys)

    Returns:
        tuple: (provider, model, temperature, thinking_level)
    """
    st.info(f"💡 **Tip:** {i18n.t('info.select_llm_tip')}")

    provider, model, thinking_level = render_provider_selection(
        current_provider=current_provider,
        current_model=current_model,
        current_thinking=current_thinking,
        show_thinking=show_thinking,
        is_defaults=is_defaults
    )

    temperature = render_temperature_input(
        value=current_temperature,
        provider=provider
    )

    return provider, model, temperature, thinking_level


def render_provider_selection(
    current_provider: str = None,
    current_model: str = None,
    current_thinking: str = None,
    show_thinking: bool = True,
    is_defaults: bool = False
) -> tuple:
    """Render LLM provider and model selection UI.

    This function provides IDENTICAL UI/UX to the Default LLM Settings page,
    ensuring consistency across all expert creation/editing interfaces.

    Args:
        current_provider: Currently selected provider (defaults to session state default)
        current_model: Currently selected model (defaults to provider default)
        current_thinking: Current thinking/reasoning level (OpenAI: "none"|"low"|"medium"|"high"|"xhigh")
        show_thinking: Whether to show thinking UI element
        is_defaults: Whether this is for default settings (affects labels and keys)

    Returns:
        tuple: (provider, model, thinking_level)
    """
    # Get defaults from session state if not provided
    if current_provider is None:
        current_provider = st.session_state.get("default_provider", "deepseek")

    if current_model is None:
        current_model = st.session_state.get("default_model", "deepseek-chat")

    # Set default thinking level if not provided
    if current_thinking is None:
        current_thinking = "none"

    # Set labels based on context
    if is_defaults:
        provider_label = i18n.t('dialogs.llm_config.default_provider')
        model_label = i18n.t('dialogs.llm_config.default_model')
        thinking_label = i18n.t('dialogs.llm_config.thinking_mode_level')
        provider_help = i18n.t('dialogs.llm_config.default_provider_help')
        model_help = i18n.t('dialogs.llm_config.default_model_help', provider="{provider}")
        thinking_help = i18n.t('dialogs.llm_config.thinking_mode_help')
        provider_key = "default_provider_selector"
        model_key = "default_model_selector"
        thinking_key = "default_thinking_slider"
    else:
        provider_label = i18n.t('forms.llm_provider')
        model_label = i18n.t('forms.model')
        thinking_label = i18n.t('default_llm.select_thinking_mode')
        provider_help = i18n.t('dialogs.llm_config.provider_help')
        model_help = i18n.t('dialogs.llm_config.model_help', provider="{provider}")
        thinking_help = i18n.t('dialogs.llm_config.thinking_mode_help_expert')
        provider_key = "expert_provider_selector"
        model_key = "expert_model_selector"
        thinking_key = "expert_thinking_slider"

    st.markdown(f"### 🤖 {i18n.t('dialogs.llm_config.title')}")

    # Provider selection
    provider_options = list(LLM_PROVIDERS.keys())
    provider_index = provider_options.index(current_provider) if current_provider in provider_options else 0

    provider = st.selectbox(
        provider_label,
        options=provider_options,
        index=provider_index,
        format_func=lambda x: get_provider_display_name(x),
        help=provider_help,
        key=provider_key
    )

    # Model selection (filtered by provider)
    model_options = list(LLM_PROVIDERS[provider]["models"].keys())

    # If current model is not in the new provider's models, use provider default
    if current_model not in model_options:
        current_model = get_default_model_for_provider(provider)

    model_index = model_options.index(current_model) if current_model in model_options else 0

    model = st.selectbox(
        model_label,
        options=model_options,
        index=model_index,
        format_func=lambda x: get_model_display_name(provider, x),
        help=model_help.format(provider=get_provider_display_name(provider)),
        key=model_key
    )

    # Display model info
    model_config = LLM_PROVIDERS[provider]["models"][model]

    # Determine UI type based on provider
    uses_reasoning_efforts = provider == "openai"
    requires_thinking = model == "deepseek-reasoner"

    # Check if provider/model supports thinking mode
    # Providers that support thinking: openai, zai (DeepSeek handled separately)
    optional_thinking_providers = {"openai", "zai"}
    supports_optional_thinking = provider in optional_thinking_providers and "thinking_param" in model_config

    st.caption(i18n.t('info.context_length', tokens=f"{model_config['max_tokens']:,}"))

    if show_thinking:
        if uses_reasoning_efforts:
            # OpenAI: Show selectbox with effort levels (use half width like temperature)
            col1, col2 = st.columns(2)
            with col1:
                effort_options = ["none", "low", "medium", "high", "xhigh"]
                effort_index = effort_options.index(current_thinking) if current_thinking in effort_options else 0
                thinking_level = st.selectbox(
                    thinking_label,
                    options=effort_options,
                    index=effort_index,
                    help=thinking_help,
                    key=thinking_key
                )

        elif supports_optional_thinking:
            # Z.AI: Show selectbox with Enabled/Disabled options (use half width like temperature)
            col1, col2 = st.columns(2)
            with col1:
                thinking_options = ["Disabled", "Enabled"]
                # Map current_thinking to index ("none" -> 0, "medium" -> 1)
                option_index = 1 if current_thinking and current_thinking != "none" else 0
                selected_option = st.selectbox(
                    thinking_label,
                    options=thinking_options,
                    index=option_index,
                    help=thinking_help,
                    key=thinking_key
                )
                # Convert back to string ("Disabled" -> "none", "Enabled" -> "medium")
                thinking_level = "medium" if selected_option == "Enabled" else "none"

        else:
            # DeepSeek or other providers: No thinking UI
            # DeepSeek-chat: no thinking support
            # DeepSeek-reasoner: thinking always enabled (handled in API layer)
            thinking_level = "none"
    else:
        # Thinking UI hidden
        thinking_level = current_thinking if current_thinking else "none"

    return provider, model, thinking_level

def create_new_expert(
    chat_name: str,
    description: str,
    temperature: float,
    custom_system_prompt: str = None,
    api_key: str = None,
    provider: str = None,
    model: str = None,
    thinking_level: str = "none"
):
    """Create a new expert agent.

    Args:
        chat_name: Name of the expert
        description: Description of expertise
        temperature: Temperature setting
        custom_system_prompt: Optional custom system prompt
        api_key: API key for AI system prompt generation (provider-specific)
        provider: LLM provider (e.g., "deepseek", "openai", "zai"). If None, uses user's default.
        model: Model to use (if None, uses provider default)
        thinking_level: Thinking/reasoning effort level ("none"|"low"|"medium"|"high"|"xhigh")

    Returns:
        tuple: (expert_id, page_path)

    Raises:
        ValueError: If an expert with the same name already exists
    """
    # Use user's default provider if not specified
    if provider is None:
        provider = get_llm_defaults()["provider"]

    config_manager = ConfigManager()
    page_generator = PageGenerator()

    # Check for duplicate expert name (case-insensitive)
    existing_experts = config_manager.list_experts()
    sanitized_input = sanitize_name(chat_name).lower()

    for expert in existing_experts:
        existing_sanitized = sanitize_name(expert["expert_name"]).lower()
        if existing_sanitized == sanitized_input:
            raise ValueError(
                f"An expert named '{chat_name}' already exists. "
                f"Please use a different name or delete the existing expert first."
            )

    # Get next page number (doesn't create file)
    page_number = page_generator.get_next_page_number()

    # Calculate expert_id
    expert_id = f"{page_number}_{sanitize_name(chat_name)}"

    # Check if AI generation will be used
    needs_ai_generation = (
        (custom_system_prompt is None or custom_system_prompt.strip() == "")
        and api_key
    )

    if needs_ai_generation:
        # Show spinner during AI generation
        with st.spinner(f"🤖 {i18n.t('dialogs.add_chat.generating_system_prompt')}"):
            config_manager.create_config(
                expert_name=chat_name,
                description=description,
                temperature=temperature,
                system_prompt=custom_system_prompt,
                api_key=api_key,
                page_number=page_number,
                provider=provider,
                model=model,
                thinking_level=thinking_level,
            )
    else:
        # No AI generation, create directly
        config_manager.create_config(
            expert_name=chat_name,
            description=description,
            temperature=temperature,
            system_prompt=custom_system_prompt,
            api_key=api_key,
            page_number=page_number,
            provider=provider,
            model=model,
            thinking_level=thinking_level,
        )

    # Generate page with correct expert_id from the start (no workaround needed!)
    page_path, _ = page_generator.generate_page(
        expert_id=expert_id,
        expert_name=chat_name,
    )

    # Clear the page index cache so navigation sees the new page
    page_generator.clear_page_cache()

    # Invalidate cache for this expert
    from lib.shared.session_state import invalidate_expert_cache
    invalidate_expert_cache(expert_id)

    return expert_id, page_path


def render_add_chat_dialog():
    """Render the Add Chat dialog.

    This dialog allows users to create a new Domain Expert Agent by providing:
    - Chat Name
    - Agent Description
    - Temperature (default: 1.0)
    - Optional: Custom System Prompt

    The dialog creates a new expert configuration and generates a dedicated page.
    """
    if not st.session_state.show_add_chat_dialog:
        return

    st.title(f"➕ {i18n.t('buttons.add_chat')}")

    # Check for API keys - at least one provider must have a key
    api_keys = st.session_state.get("api_keys", {})
    api_key_available = any(api_keys.values())

    if not api_key_available:
        st.warning(f"""
        ⚠️ **{i18n.t('dialogs.add_chat.api_key_required')}**

        {i18n.t('dialogs.add_chat.api_key_required_desc')}
        """)

        if st.button(f"🔧 {i18n.t('buttons.go_to_settings')}", type="primary"):
            st.switch_page("pages/9998_Settings.py")

        return

    # LLM Configuration (Provider, Model, Temperature, Thinking)
    provider, model, temperature, thinking_level = render_llm_configuration()

    st.divider()

    with st.form("add_chat_form"):
        st.subheader(i18n.t('dialogs.add_chat.expert_configuration'))

        # Chat Name
        chat_name = st.text_input(
            f"{i18n.t('forms.expert_name')} *",
            placeholder=i18n.t('forms.expert_name_placeholder'),
            help=i18n.t('dialogs.add_chat.help_expert_name'),
            max_chars=100,
        ).strip()

        # Add caption with allowed characters
        st.caption(f"💡 **{i18n.t('forms.allowed_characters')}:** {i18n.t('forms.allowed_characters_desc')}")

        # Agent Description
        description = st.text_area(
            f"{i18n.t('forms.agent_description')} *",
            placeholder=i18n.t('forms.agent_description_placeholder'),
            help=i18n.t('dialogs.add_chat.help_expert_description'),
            height="content",
            max_chars=1000,
        ).strip()

        st.divider()

        # Expert Behavior (Advanced) - The most important field!
        st.markdown(f"### 🧠 {i18n.t('dialogs.add_chat.expert_behavior_title')}")
        st.caption(
            f"💡 {i18n.t('info.ai_powered_tip')}"
        )

        custom_system_prompt = st.text_area(
            i18n.t('forms.custom_system_prompt'),
            placeholder=i18n.t('forms.custom_system_prompt_placeholder'),
            help=i18n.t('dialogs.add_chat.help_custom_behavior'),
            height=250,
            max_chars=3000,
        ).strip()

        # Inform users about automatic language response
        st.caption(f"💡 {i18n.t('info.language_prefix_auto')}")

        # Add expander with examples
        with st.expander(f"📖 {i18n.t('dialogs.add_chat.why_important_title')}"):
            st.markdown(get_expert_behavior_docs())

        st.caption(i18n.t('info.required_fields_hint'))

        # Form buttons (left-aligned)
        st.write("")  # Spacing
        col1, col2, col3 = st.columns([1, 1, 6])

        with col1:
            submit_button = st.form_submit_button(i18n.t("buttons.create_expert"), type="primary")

        with col2:
            cancel_button = st.form_submit_button(i18n.t("buttons.cancel"))

        # Handle form submission
        if submit_button:
            # Validate required fields
            if not chat_name or not description:
                st.error(i18n.t("errors.required_fields"))
                return

            # Validate expert name
            is_valid, error_msg = validate_expert_name(chat_name)
            if not is_valid:
                st.error(f"❌ {error_msg}")
                return

            try:
                # Get API key for system prompt generation (provider-specific)
                api_keys = st.session_state.get("api_keys", {})
                api_key = api_keys.get(provider, None)

                if not api_key:
                    provider_name = get_provider_display_name(provider)
                    st.error(i18n.t("status.no_api_key", provider=provider_name))
                    return

                expert_id, page_path = create_new_expert(
                    chat_name,
                    description,
                    temperature,
                    custom_system_prompt,
                    api_key,
                    provider,
                    model,
                    thinking_level
                )

                # Store the page path for navigation after rerun
                st.session_state.pending_expert_page = page_path
                st.session_state.show_add_chat_dialog = False

                st.success(i18n.t("success.expert_created", name=chat_name))
                st.info("🔄 " + i18n.t("info.navigating"))

                # Rerun to let Streamlit discover the new page
                st.rerun()

            except ValueError as e:
                # Show user-friendly error in UI
                st.error(i18n.t("errors.expert_exists", name=chat_name))
            except Exception as e:
                # Show user-friendly error in UI
                st.error(f"❌ {i18n.t('errors.error_creating_expert')}: {str(e)}")

        if cancel_button:
            st.session_state.show_add_chat_dialog = False
            st.rerun()
