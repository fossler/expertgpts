"""Domain Expert Agent Chat Template.

This template is used to generate individual expert pages.
Replace 20251231_010519_translation_expert and Translation Expert when generating new pages.
"""

import os
import streamlit as st
from utils.config_manager import ConfigManager
from utils.deepseek_client import DeepSeekClient


# Expert Configuration
EXPERT_ID = "20251231_010519_translation_expert"
EXPERT_NAME = "Translation Expert"


def initialize_session_state():
    """Initialize session state variables."""
    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Initialize API key in session state (from environment or existing session)
    if "deepseek_api_key" not in st.session_state:
        env_api_key = os.getenv("DEEPSEEK_API_KEY")
        st.session_state.deepseek_api_key = env_api_key or ""

    return messages_key


def load_expert_config() -> dict:
    """Load the expert configuration.

    Returns:
        Configuration dictionary
    """
    config_manager = ConfigManager()

    try:
        config = config_manager.load_config(EXPERT_ID)
        return config
    except FileNotFoundError:
        st.error(f"Configuration not found for expert: {EXPERT_ID}")
        return {}


def render_sidebar() -> str:
    """Render the sidebar with API key input and links.

    Returns:
        API key from session state
    """
    with st.sidebar:
        st.title("⚙️ Settings")

        # API Key status display
        if st.session_state.deepseek_api_key:
            st.success("✅ API key configured")
            st.caption("🔑 Available to all experts")
        else:
            st.warning("⚠️ API key not set")
            st.caption("Enter your API key below to use this expert")

        # API Key input (can override existing key)
        api_key = st.text_input(
            "DeepSeek API Key",
            key=f"api_key_{EXPERT_ID}",
            type="password",
            value=st.session_state.deepseek_api_key if st.session_state.deepseek_api_key else "",
            help="Enter your API key. It will be shared across all expert pages.",
            placeholder="Enter your API key",
        )

        # Update session state if user entered/changed the key
        if api_key and api_key != st.session_state.deepseek_api_key:
            st.session_state.deepseek_api_key = api_key
            st.success("✅ API key updated!")
            st.rerun()

        st.divider()

        # Footer links
        st.caption("**Resources**")
        "[Get a DeepSeek API key](https://platform.deepseek.com/)"
        "[DeepSeek API Documentation](https://api-docs.deepseek.com/)"
        "[View the source code](https://github.com/yourusername/deepagents)"

        st.divider()

    return st.session_state.deepseek_api_key


def render_chat_interface(config: dict, messages_key: str):
    """Render the main chat interface.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    st.title(f"🤖 {config.get('expert_name', EXPERT_NAME)}")

    # Display expert description
    if config.get("description"):
        st.markdown(f"*{config['description']}*")
        st.divider()

    # Display chat messages
    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(api_key: str, config: dict, messages_key: str):
    """Handle user input and generate assistant response.

    Args:
        api_key: DeepSeek API key
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    if prompt := st.chat_input("Ask the expert..."):
        # Check API key
        if not api_key:
            st.error("Please enter your DeepSeek API key in the sidebar.")
            return

        # Add user message to chat history
        st.session_state[messages_key].append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                # Initialize DeepSeek client
                client = DeepSeekClient(api_key=api_key)

                # Convert messages to format expected by API
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state[messages_key]
                ]

                # Stream response
                response = ""
                for chunk in client.chat_stream(
                    messages=api_messages,
                    temperature=config.get("temperature", 1.0),
                    system_prompt=config.get("system_prompt"),
                ):
                    response += chunk
                    message_placeholder.markdown(response + "▌")

                message_placeholder.markdown(response)

                # Add assistant response to chat history
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": error_msg
                })


def clear_chat_history(messages_key: str):
    """Clear the chat history for this expert.

    Args:
        messages_key: Session state key for this expert's messages
    """
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state[messages_key] = []
        st.rerun()


def main():
    """Main application entry point."""
    messages_key = initialize_session_state()

    # Load expert configuration
    config = load_expert_config()

    if not config:
        st.error("Failed to load expert configuration.")
        return

    # Render sidebar
    api_key = render_sidebar()

    # Clear chat button
    clear_chat_history(messages_key)

    # Render main interface
    render_chat_interface(config, messages_key)

    # Handle user input
    handle_user_input(api_key, config, messages_key)


if __name__ == "__main__":
    main()
