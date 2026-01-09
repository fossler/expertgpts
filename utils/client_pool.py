"""LLM Client connection pooling for performance optimization.

This module provides a centralized client pool that caches LLM client instances
to avoid repeated initialization overhead. Clients are keyed by provider and
a hash of the API key (for security).
"""

import hashlib
import streamlit as st
from typing import Dict, Optional
from utils.llm_client import LLMClient


class ClientPool:
    """Pool for caching and reusing LLM client instances."""

    # Class-level cache (not session-specific)
    _clients: Dict[str, LLMClient] = {}

    @classmethod
    def get_client(cls, provider: str, api_key: str) -> LLMClient:
        """Get or create a cached LLM client instance.

        Args:
            provider: Provider key (e.g., "deepseek", "openai", "zai")
            api_key: API key for the provider

        Returns:
            LLMClient: Cached or newly created client instance

        Example:
            >>> client = ClientPool.get_client("deepseek", "sk-abc123")
            >>> response = client.chat_stream(messages, temperature=0.7)
        """
        # Create a safe cache key (don't store full API key in memory)
        cache_key = cls._create_cache_key(provider, api_key)

        # Check cache
        if cache_key in cls._clients:
            return cls._clients[cache_key]

        # Create new client and cache it
        client = LLMClient(provider=provider, api_key=api_key)
        cls._clients[cache_key] = client
        return client

    @classmethod
    def _create_cache_key(cls, provider: str, api_key: str) -> str:
        """Create a safe cache key from provider and API key.

        Uses a hash of the API key to avoid storing sensitive data in memory.

        Args:
            provider: Provider key
            api_key: API key

        Returns:
            str: Cache key (e.g., "deepseek_a1b2c3d4")
        """
        # Hash the API key for security (don't store full key)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:8]
        return f"{provider}_{key_hash}"

    @classmethod
    def clear_cache(cls):
        """Clear all cached clients.

        Useful for testing or when API keys change.
        """
        cls._clients.clear()

    @classmethod
    def remove_client(cls, provider: str, api_key: str):
        """Remove a specific client from the cache.

        Args:
            provider: Provider key
            api_key: API key
        """
        cache_key = cls._create_cache_key(provider, api_key)
        cls._clients.pop(cache_key, None)

    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Get statistics about the client pool cache.

        Returns:
            dict: Statistics including total clients and clients per provider
        """
        stats = {
            "total_clients": len(cls._clients),
            "providers": {}
        }

        for cache_key in cls._clients.keys():
            provider = cache_key.split("_")[0]
            stats["providers"][provider] = stats["providers"].get(provider, 0) + 1

        return stats


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


# Convenience function for backward compatibility
def get_client(provider: str, api_key: str, use_streamlit_cache: bool = True) -> LLMClient:
    """Get an LLM client (with automatic caching).

    This is the recommended way to get client instances in your code.

    Args:
        provider: Provider key (e.g., "deepseek", "openai", "zai")
        api_key: API key for the provider
        use_streamlit_cache: If True, use Streamlit's @st.cache_resource
                            If False, use manual ClientPool

    Returns:
        LLMClient: Cached client instance

    Example:
        >>> from utils.client_pool import get_client
        >>> client = get_client("deepseek", api_key)
        >>> response = client.chat_stream(messages, temperature=0.7)
    """
    if use_streamlit_cache:
        return get_cached_client(provider, api_key)
    else:
        return ClientPool.get_client(provider, api_key)
