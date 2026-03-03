"""LLM Client connection caching for performance optimization.

This module provides a Streamlit-cached client getter that caches LLM client
instances to avoid repeated initialization overhead.
"""

import streamlit as st
from lib.llm.llm_client import LLMClient


@st.cache_resource
def get_cached_client(provider: str, api_key: str) -> LLMClient:
    """Streamlit-cached client getter with resource-level caching.

    This function uses Streamlit's @st.cache_resource decorator to cache
    client instances across reruns, providing even better performance than
    manual caching.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        api_key: API key for the provider

    Returns:
        LLMClient: Cached client instance

    Example:
        >>> client = get_cached_client("deepseek", "sk-abc123")
        >>> response = client.chat_stream(messages, temperature=0.7)

    Note:
        This uses Streamlit's cache_resource which is ideal for objects
        that are safe to reuse across reruns (like HTTP clients).
    """
    return LLMClient(provider=provider, api_key=api_key)
