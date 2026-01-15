"""ExpertGPTs - Home Page.

Welcome page for the ExpertGPTs multi-expert AI chat application.
"""

import streamlit as st
from utils.config_manager import ConfigManager
from utils.dialogs import render_add_chat_dialog
from utils.i18n import i18n


def render_expert_list():
    """Render a list of available expert agents."""
    config_manager = ConfigManager()
    experts = config_manager.list_experts()

    if not experts:
        st.info(f"🔍 {i18n.t('home.no_experts')}")
        return

    st.subheader(f"📚 {i18n.t('home.available_experts')}")

    # Display experts in a grid
    cols = st.columns(min(3, len(experts)))

    for idx, expert in enumerate(experts):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {expert['expert_name']}")
                display_desc = expert['description'][:100] + "..." if len(expert['description']) > 100 else expert['description']
                st.caption(display_desc)
                st.caption(f"🆔 {expert['expert_id']}")


def main():
    """Render the home page content."""
    # Render sidebar
    with st.sidebar:
        # Toolbox
        st.caption(f"**{i18n.t('home.toolbox')}**")
        if st.button(f"➕ {i18n.t('buttons.add_chat')}", width="stretch"):
            st.session_state.show_add_chat_dialog = True
            st.rerun()

        st.divider()

        # Status section
        st.caption(f"**{i18n.t('home.status')}**")

        # API Key status (check if any provider key is set)
        api_keys = st.session_state.get("api_keys", {})
        if any(api_keys.values()):
            st.success(f"✅ {i18n.t('status.api_key_configured')}")
        else:
            st.caption(f"⚠️ {i18n.t('status.api_key_not_set')}")

        st.divider()

    # Render add chat dialog if active
    if st.session_state.show_add_chat_dialog:
        render_add_chat_dialog()
        return

    st.title(f"🤖 {i18n.t('home.title')}")

    st.markdown(f"""
    ## {i18n.t('home.subtitle')}

    ExpertGPTs provides access to multiple domain-specific expert AI agents, each specialized
    in different fields. Select an expert from the navigation menu to start chatting!

    ### {i18n.t('home.getting_started')}

    1. **{i18n.t('home.getting_started_steps.step1')}**: {i18n.t('home.getting_started_steps.step1_desc')}
    2. **{i18n.t('home.getting_started_steps.step2')}**: {i18n.t('home.getting_started_steps.step2_desc')}
    3. **{i18n.t('home.getting_started_steps.step3')}**: {i18n.t('home.getting_started_steps.step3_desc')}

    ### {i18n.t('home.create_custom_experts')}

    {i18n.t('home.create_experts_desc')}
    - {i18n.t('home.expert_features.feature1')}
    - {i18n.t('home.expert_features.feature2')}
    - {i18n.t('home.expert_features.feature3')}

    ### {i18n.t('home.features.title')}

    - 🎯 **{i18n.t('home.features.domain_expertise')}**: {i18n.t('home.features.domain_expertise_desc')}
    - 🔧 **{i18n.t('home.features.customizable')}**: {i18n.t('home.features.customizable_desc')}
    - 🌡️ **{i18n.t('home.features.temperature')}**: {i18n.t('home.features.temperature_desc')}
    - 💾 **{i18n.t('home.features.chat_history')}**: {i18n.t('home.features.chat_history_desc')}
    - 🔐 **{i18n.t('home.features.secure_secrets')}**: {i18n.t('home.features.secure_secrets_desc')}
    - 🎨 **{i18n.t('home.features.custom_themes')}**: {i18n.t('home.features.custom_themes_desc')}
    """)

    st.divider()

    # Show expert list
    render_expert_list()


if __name__ == "__main__":
    main()
