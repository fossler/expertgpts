"""Shared dialog rendering functions for ExpertGPTs application.

This module contains reusable dialog components to avoid code duplication
across multiple pages.
"""

import re
import streamlit as st
from utils.config_manager import ConfigManager
from utils.constants import EXPERT_BEHAVIOR_DOCS
from utils.page_generator import PageGenerator
from utils import debug_logger


def validate_expert_name(name: str) -> tuple[bool, str]:
    """Validate expert name for alphanumerics and special characters.

    Args:
        name: Expert name to validate

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


def render_temperature_input(value: float = 1.0) -> float:
    """Render temperature input field with reduced width (1/8 of normal).

    Args:
        value: Current temperature value (default: 1.0)

    Returns:
        float: Temperature value from user input
    """
    # Create columns to control width (1/8 of normal) - temperature on LEFT
    temp_col, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    with temp_col:
        temperature = st.number_input(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=value,
            step=0.1,
            help="Controls randomness in responses. Lower = more focused, Higher = more creative",
            label_visibility="visible",
        )

    return temperature


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
    config_manager = ConfigManager()
    page_generator_obj = PageGenerator()

    # Get API key from session state for AI generation
    api_key = st.session_state.get("deepseek_api_key", None)

    # Check if AI generation will be used
    needs_ai_generation = (
        (custom_system_prompt is None or custom_system_prompt.strip() == "")
        and api_key
    )

    if needs_ai_generation:
        # Show spinner during AI generation
        with st.spinner("🤖 Generating AI-powered system prompt..."):
            expert_id = config_manager.create_config(
                expert_name=chat_name,
                description=description,
                temperature=temperature,
                system_prompt=custom_system_prompt,
                api_key=api_key,
            )
    else:
        # No AI generation, create directly
        expert_id = config_manager.create_config(
            expert_name=chat_name,
            description=description,
            temperature=temperature,
            system_prompt=custom_system_prompt,
            api_key=api_key,
        )

    # Generate page
    page_path = page_generator_obj.generate_page(
        expert_id=expert_id,
        expert_name=chat_name,
    )

    # Invalidate cache for this expert
    if f"cache_version_{expert_id}" not in st.session_state:
        st.session_state[f"cache_version_{expert_id}"] = 0
    st.session_state[f"cache_version_{expert_id}"] += 1

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

    st.title("➕ Add New Expert Chat")

    # Check for API key - required for expert creation
    api_key_available = bool(st.session_state.get("deepseek_api_key", ""))

    if not api_key_available:
        st.warning("""
        ⚠️ **API Key Required**

        New chats can only be created when an API key is defined.

        Please set your DeepSeek API key in **Settings → API Key** tab first.
        """)

        if st.button("🔧 Go to Settings", type="primary"):
            st.switch_page("pages/9999_Settings.py")

        return

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
            "💡 **AI-powered generation!** Leave empty to auto-generate a customized "
            "system prompt based on the description above. "
            "Provide your own for complete control."
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
                expert_id, page_path = create_new_expert(chat_name, description, temperature, custom_system_prompt)

                # Store the page path for navigation after rerun
                st.session_state.pending_expert_page = page_path
                st.session_state.show_add_chat_dialog = False

                st.success(f"✅ Expert '{chat_name}' created successfully!")
                st.info("🔄 Navigating to your new expert...")

                # Rerun to let Streamlit discover the new page
                st.rerun()

            except Exception as e:
                # Log detailed error to file
                debug_logger.log_exception(
                    exception=e,
                    context={
                        "function": "create_new_expert",
                        "chat_name": chat_name,
                        "description": description[:100] if description else None,
                        "temperature": temperature,
                        "custom_system_prompt_provided": custom_system_prompt is not None,
                        "api_key_available": bool(st.session_state.get("deepseek_api_key", "")),
                        "show_modules": True  # Show loaded modules for import debugging
                    },
                    log_file="expert_creation_errors.log"
                )

                # Show user-friendly error in UI
                st.error(f"❌ Error creating expert: {str(e)}")
                st.info("📝 Detailed error has been logged to `logs/expert_creation_errors.log`")

        if cancel_button:
            st.session_state.show_add_chat_dialog = False
            st.rerun()
