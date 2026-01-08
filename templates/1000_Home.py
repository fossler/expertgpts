"""ExpertGPTs - Home Page.

Welcome page for the ExpertGPTs multi-expert AI chat application.
"""

import streamlit as st
from utils.config_manager import ConfigManager
from utils.dialogs import render_add_chat_dialog


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

        # API Key status (check if any provider key is set)
        api_keys = st.session_state.get("api_keys", {})
        if any(api_keys.values()):
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
