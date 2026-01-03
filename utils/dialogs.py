"""Shared dialog rendering functions for ExpertGPTs application.

This module contains reusable dialog components to avoid code duplication
across multiple pages.
"""

import re
import streamlit as st
from utils.config_manager import ConfigManager
from utils.constants import EXPERT_BEHAVIOR_DOCS
from utils.page_generator import PageGenerator
from utils.helpers import sanitize_name


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
            help="Controls response creativity and focus",
            label_visibility="visible",
        )

        # Add expander with detailed temperature guidance
        with st.expander("📖 Recommended values", expanded=False):
            st.markdown("""
            **Use Case Guidelines:**

            • **0.0** - Coding/Math (precision required)
            • **1.0** - Data Analysis (balanced interpretation)
            • **1.3** - Conversation/Translation (natural communication)
            • **1.5** - Creative Writing/Poetry (maximum creativity)

            *Based on official DeepSeek documentation*
            """)

    return temperature


def create_new_expert(
    chat_name: str,
    description: str,
    temperature: float,
    custom_system_prompt: str = None,
    api_key: str = None
):
    """Create a new expert agent.

    Args:
        chat_name: Name of the expert
        description: Description of expertise
        temperature: Temperature setting
        custom_system_prompt: Optional custom system prompt
        api_key: DeepSeek API key for AI system prompt generation

    Returns:
        tuple: (expert_id, page_path)

    Raises:
        ValueError: If an expert with the same name already exists
    """
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
        with st.spinner("🤖 Generating AI-powered system prompt..."):
            config_manager.create_config(
                expert_name=chat_name,
                description=description,
                temperature=temperature,
                system_prompt=custom_system_prompt,
                api_key=api_key,
                page_number=page_number,
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
        )

    # Generate page with correct expert_id from the start (no workaround needed!)
    page_path, _ = page_generator.generate_page(
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
                # Show user-friendly error in UI
                st.error(f"❌ Error creating expert: {str(e)}")

        if cancel_button:
            st.session_state.show_add_chat_dialog = False
            st.rerun()
