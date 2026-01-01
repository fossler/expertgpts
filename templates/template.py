"""Domain Expert Agent Chat Template.

This template is used to generate individual expert pages.
Replace {{EXPERT_ID}} and {{EXPERT_NAME}} when generating new pages.
"""

import streamlit as st
import tiktoken
from utils.config_manager import ConfigManager
from utils.deepseek_client import DeepSeekClient
from utils.session_state import initialize_shared_session_state


# Expert Configuration
EXPERT_ID = "{{EXPERT_ID}}"
EXPERT_NAME = "{{EXPERT_NAME}}"


def initialize_session_state():
    """Initialize session state variables."""
    # Initialize shared state first (API key, navigation, etc.)
    initialize_shared_session_state()

    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    return messages_key


@st.cache_data(ttl=300, show_spinner="Loading expert configuration...")
def load_expert_config_cached(expert_id: str, cache_version: int = 0) -> dict:
    """Load and cache the expert configuration.

    Args:
        expert_id: Unique ID of the expert
        cache_version: Version to invalidate cache when config is edited

    Returns:
        Configuration dictionary
    """
    config_manager = ConfigManager()

    try:
        config = config_manager.load_config(expert_id)
        return config
    except FileNotFoundError:
        return {}


def load_expert_config() -> dict:
    """Load the expert configuration with cache support.

    Returns:
        Configuration dictionary
    """
    # Get cache version from session state (incremented when config is edited)
    cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)

    config = load_expert_config_cached(EXPERT_ID, cache_version)

    if not config:
        st.error(f"Configuration not found for expert: {EXPERT_ID}")

    return config




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
            st.error("Please enter your DeepSeek API key in the Settings page.")
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

                # Rerun to update context usage with new message
                st.rerun()

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.rerun()


def clear_chat_history(messages_key: str):
    """Clear the chat history for this expert.

    Args:
        messages_key: Session state key for this expert's messages
    """
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state[messages_key] = []
        st.rerun()


@st.cache_resource
def get_encoding():
    """Get and cache the tiktoken encoding for DeepSeek.

    Uses cl100k_base encoding (same as GPT-3.5/4).

    Returns:
        Tiktoken encoding object
    """
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, encoding) -> int:
    """Count tokens in a text string.

    Args:
        text: Text to count tokens for
        encoding: Tiktoken encoding

    Returns:
        Number of tokens
    """
    return len(encoding.encode(text))


def display_context_usage(config: dict, messages_key: str):
    """Display context length usage in the sidebar.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Get the cached encoding for DeepSeek
    try:
        encoding = get_encoding()
    except Exception:
        # Fallback if tiktoken fails
        st.sidebar.caption("ℹ️ Token counting unavailable")
        return

    # Count tokens in system prompt
    system_prompt = config.get("system_prompt", "")
    system_tokens = count_tokens(system_prompt, encoding) if system_prompt else 0

    # Count tokens in chat messages
    messages = st.session_state.get(messages_key, [])
    messages_tokens = 0
    for message in messages:
        messages_tokens += count_tokens(message.get("content", ""), encoding)

    # Total tokens
    total_tokens = system_tokens + messages_tokens

    # DeepSeek max context is 128K tokens
    max_tokens = 128000
    usage_percent = (total_tokens / max_tokens) * 100

    # Display context usage in sidebar
    st.sidebar.markdown("### 📊 Context Usage")

    # Choose color based on usage
    if usage_percent < 50:
        color = "🟢"
    elif usage_percent < 75:
        color = "🟡"
    elif usage_percent < 90:
        color = "🟠"
    else:
        color = "🔴"

    st.sidebar.markdown(f"{color} **{usage_percent:.1f}%** of 128K tokens")
    st.sidebar.caption(f"Total: {total_tokens:,} / {max_tokens:,} tokens")

    # Show breakdown
    with st.sidebar.expander("See breakdown"):
        st.caption(f"📝 System Prompt: {system_tokens:,} tokens")
        st.caption(f"💬 Chat Messages: {messages_tokens:,} tokens")

    st.sidebar.divider()


def main():
    """Main application entry point."""
    messages_key = initialize_session_state()

    # Load expert configuration
    config = load_expert_config()

    if not config:
        st.error("Failed to load expert configuration.")
        return

    # Get API key from session state
    api_key = st.session_state.deepseek_api_key

    # Display context usage in sidebar (before clear button)
    display_context_usage(config, messages_key)

    # Clear chat button (in sidebar)
    clear_chat_history(messages_key)

    # Render main interface
    render_chat_interface(config, messages_key)

    # Handle user input
    handle_user_input(api_key, config, messages_key)


if __name__ == "__main__":
    main()
