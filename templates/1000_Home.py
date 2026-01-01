"""ExpertGPTs - Home Page.

Welcome page for the ExpertGPTs multi-expert AI chat application.
"""

import re
import streamlit as st
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator


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
        temperature = st.number_input(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Controls randomness in responses. Lower = more focused, Higher = more creative",
        )

        # System Prompt
        custom_system_prompt = st.text_area(
            "System Prompt",
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
                st.error(f"❌ Error creating expert: {str(e)}")

        if cancel_button:
            st.session_state.show_add_chat_dialog = False
            st.rerun()


def render_expert_list():
    """Render a list of available expert agents."""
    config_manager = ConfigManager()
    experts = config_manager.list_experts()

    if not experts:
        st.info("🔍 No expert agents found. Create your first expert from Settings!")
        return

    st.subheader("📚 Available Expert Agents")

    # Display experts in a grid
    cols = st.columns(min(3, len(experts)))

    for idx, expert in enumerate(experts):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {expert['expert_name']}")
                st.caption(expert['description'][:100] + "..." if len(expert['description']) > 100 else expert['description'])
                st.caption(f"🆔 {expert['expert_id']}")


def main():
    """Render the home page content."""
    # Render sidebar
    with st.sidebar:
        # Toolbox
        st.caption("**Toolbox**")
        if st.button("➕ Add Chat", width="stretch"):
            st.session_state.show_add_chat_dialog = True
            st.rerun()

        st.divider()

        # Status section
        st.caption("**Status**")

        # API Key status
        if st.session_state.deepseek_api_key:
            st.success("✅ API key configured")
        else:
            st.caption("⚠️ API key not set")

        st.divider()

    # Render add chat dialog if active
    if st.session_state.show_add_chat_dialog:
        render_add_chat_dialog()
        return

    st.title("🤖 Welcome to ExpertGPTs")

    st.markdown("""
    ## Your Multi-Expert AI Assistant Platform

    ExpertGPTs provides access to multiple domain-specific expert AI agents, each specialized
    in different fields. Select an expert from the navigation menu to start chatting!

    ### Getting Started

    1. **Set your API Key**: Enter your DeepSeek API key in Settings (it will be saved securely)
    2. **Choose an Expert**: Select an expert agent from the navigation menu
    3. **Start Chatting**: Ask questions and get expert-level responses

    ### Create Custom Experts

    Click the **"➕ Add Chat"** button in the sidebar to create your own domain-specific experts:
    - Define the expert's name and specialization
    - Set the temperature for response creativity
    - Optionally provide a custom system prompt

    ### Features

    - 🎯 **Domain-Specific Expertise**: Each expert specializes in a specific domain
    - 🔧 **Customizable**: Create experts tailored to your needs
    - 🌡️ **Adjustable Temperature**: Control response creativity and focus
    - 💾 **Chat History**: Maintain conversation context throughout your session
    - 🔐 **Secure Secrets**: API keys stored in `.streamlit/secrets.toml`
    - 🎨 **Customizable Themes**: Personalize the app appearance
    """)

    st.divider()

    # Show expert list
    render_expert_list()


if __name__ == "__main__":
    main()
