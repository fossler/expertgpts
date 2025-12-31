"""DeepAgents - Multi-Expert AI Chat Application.

A Streamlit application that provides access to multiple domain-specific
expert AI agents powered by DeepSeek API.
"""

import os
from pathlib import Path
import streamlit as st
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator


# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        pass  # python-dotenv not installed, continue without it


st.set_page_config(
    page_title="DeepAgents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Initialize session state variables."""
    if "show_add_chat_dialog" not in st.session_state:
        st.session_state.show_add_chat_dialog = False

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


def render_sidebar():
    """Render the sidebar with navigation and tools.

    The sidebar contains:
    - Expert navigation (automatic via Streamlit)
    - Toolbox with "Add Chat" button
    - Footer with API key input and links
    """
    with st.sidebar:

        # Toolbox
        st.caption("**Toolbox**")
        if st.button("➕ Add Chat", use_container_width=True):
            st.session_state.show_add_chat_dialog = True

        st.divider()

        # Footer
        st.caption("**Status**")

        # API Key status
        if st.session_state.deepseek_api_key:
            st.success("✅ API key configured")
        else:
            st.caption("⚠️ API key not set")

        st.divider()

    return st.session_state.deepseek_api_key


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
            height=150,
            max_chars=1000,
        ).strip()

        # Temperature
        temperature = st.slider(
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
                height=150,
                help="Provide a custom system prompt for this expert",
                max_chars=2000,
            ).strip()

        st.caption("* Required fields")

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submit_button = st.form_submit_button("Create Expert", use_container_width=True, type="primary")

        with col2:
            cancel_button = st.form_submit_button("Cancel", use_container_width=True)

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


def render_expert_list():
    """Render a list of available expert agents."""
    config_manager = ConfigManager()
    experts = config_manager.list_experts()

    if not experts:
        st.info("🔍 No expert agents found. Create your first expert using the 'Add Chat' button!")
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


def render_main_content():
    """Render the main page content."""
    st.title("🤖 Welcome to DeepAgents")

    st.markdown("""
    ## Your Multi-Expert AI Assistant Platform

    DeepAgents provides access to multiple domain-specific expert AI agents, each specialized
    in different fields. Select an expert from the navigation menu above to start chatting!

    ### Getting Started

    1. **Set your API Key**: Enter your DeepSeek API key in the sidebar
    2. **Choose an Expert**: Select an expert agent from the navigation menu
    3. **Start Chatting**: Ask questions and get expert-level responses

    ### Create Custom Experts

    Use the **Add Chat** button in the sidebar to create your own domain-specific experts:
    - Define the expert's name and specialization
    - Set the temperature for response creativity
    - Optionally provide a custom system prompt

    ### Features

    - 🎯 **Domain-Specific Expertise**: Each expert specializes in a specific domain
    - 🔧 **Customizable**: Create experts tailored to your needs
    - 🌡️ **Adjustable Temperature**: Control response creativity and focus
    - 💾 **Chat History**: Maintain conversation context throughout your session
    """)

    st.divider()

    # Show expert list
    render_expert_list()


def main():
    """Main application entry point."""
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Render add chat dialog if active
    if st.session_state.show_add_chat_dialog:
        render_add_chat_dialog()
    else:
        # Render main content
        render_main_content()


if __name__ == "__main__":
    main()
