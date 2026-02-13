"""Token counting and context usage management for DeepSeek API.

This module provides centralized token management functionality including
counting, caching, and usage statistics calculation.
"""

import hashlib
import streamlit as st
import tiktoken
from lib.shared.constants import (
    DEEPSEEK_MAX_CONTEXT_TOKENS,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS,
    SYSTEM_PROMPT_CACHE_TTL,
    TOKEN_COUNT_CACHE_TTL
)


def get_messages_hash(messages: list) -> str:
    """Generate hash of message content for cache invalidation.

    Creates a lightweight hash based on message count and total
    content length. Fast to compute but changes when messages change.

    Args:
        messages: List of chat messages

    Returns:
        8-character hex hash string
    """
    total_length = sum(len(str(msg.get("content", ""))) for msg in messages)
    msg_count = len(messages)

    # Create hash from count and length (changes when messages change)
    hash_input = f"{msg_count}:{total_length}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:8]


class TokenManager:
    """Manages token counting and context usage for DeepSeek API."""

    @staticmethod
    @st.cache_resource
    def get_encoding():
        """Get and cache the tiktoken encoding for DeepSeek.

        Uses cl100k_base encoding (same as GPT-3.5/4).

        Returns:
            Tiktoken encoding object
        """
        return tiktoken.get_encoding("cl100k_base")

    @staticmethod
    def count_tokens(text: str, encoding=None) -> int:
        """Count tokens in a text string.

        Args:
            text: Text to count tokens for
            encoding: Optional pre-loaded encoding (for batch processing)

        Returns:
            Number of tokens
        """
        if encoding is None:
            encoding = TokenManager.get_encoding()
        return len(encoding.encode(text))

    @staticmethod
    @st.cache_data(ttl=SYSTEM_PROMPT_CACHE_TTL, show_spinner=False)
    def count_system_prompt_tokens(system_prompt: str) -> int:
        """Count tokens in system prompt (cached).

        Args:
            system_prompt: System prompt text

        Returns:
            Token count (0 if empty)

        This function is cached to avoid recounting the same system prompt
        on every rerun, as system prompts rarely change during a session.
        """
        if not system_prompt:
            return 0
        encoding = TokenManager.get_encoding()
        return TokenManager.count_tokens(system_prompt, encoding)

    @staticmethod
    @st.cache_data(ttl=TOKEN_COUNT_CACHE_TTL, show_spinner=False)
    def count_messages_tokens(messages_key: str, messages_hash: str, _messages: list) -> int:
        """Count tokens in chat messages (cached).

        Args:
            messages_key: Session state key for this expert's messages
            messages_hash: Hash of message content for invalidation
            _messages: List of chat messages (underscore = not part of cache key)

        Returns:
            Total token count

        This function is cached to avoid recounting messages on every rerun.
        The cache automatically invalidates when:
        - TTL expires
        - messages_key changes (different expert)
        - messages_hash changes (message content changed)
        """
        encoding = TokenManager.get_encoding()
        return sum(
            TokenManager.count_tokens(msg.get("content", ""), encoding)
            for msg in _messages
        )

    @staticmethod
    def calculate_usage_statistics(
        system_prompt: str,
        messages: list,
        max_tokens: int = DEEPSEEK_MAX_CONTEXT_TOKENS
    ) -> dict:
        """Calculate comprehensive token usage statistics.

        Args:
            system_prompt: System prompt text
            messages: List of chat messages
            max_tokens: Maximum context window size

        Returns:
            Dictionary with usage statistics:
            {
                "total_tokens": int,
                "usage_percent": float,
                "system_tokens": int,
                "messages_tokens": int,
                "color": str (emoji),
                "max_tokens": int
            }
            or {"error": str, "total_tokens": 0, "usage_percent": 0} on error
        """
        try:
            encoding = TokenManager.get_encoding()
        except (ImportError, OSError, ValueError) as e:
            return {
                "error": f"Token counting unavailable: {type(e).__name__}",
                "total_tokens": 0,
                "usage_percent": 0
            }

        # Count tokens in system prompt
        system_tokens = (
            TokenManager.count_tokens(system_prompt, encoding)
            if system_prompt else 0
        )

        # Count tokens in chat messages
        messages_tokens = sum(
            TokenManager.count_tokens(msg.get("content", ""), encoding)
            for msg in messages
        )

        # Calculate totals
        total_tokens = system_tokens + messages_tokens
        usage_percent = (total_tokens / max_tokens) * 100

        # Determine color based on usage
        if usage_percent < CONTEXT_USAGE_SAFE_THRESHOLD:
            color = CONTEXT_USAGE_COLORS["safe"]
        elif usage_percent < CONTEXT_USAGE_WARNING_THRESHOLD:
            color = CONTEXT_USAGE_COLORS["warning"]
        elif usage_percent < CONTEXT_USAGE_ALERT_THRESHOLD:
            color = CONTEXT_USAGE_COLORS["alert"]
        else:
            color = CONTEXT_USAGE_COLORS["critical"]

        return {
            "total_tokens": total_tokens,
            "usage_percent": usage_percent,
            "system_tokens": system_tokens,
            "messages_tokens": messages_tokens,
            "color": color,
            "max_tokens": max_tokens
        }

    @staticmethod
    def get_usage_color(usage_percent: float) -> str:
        """Get emoji color based on usage percentage.

        Args:
            usage_percent: Usage percentage (0-100)

        Returns:
            Emoji color indicator
        """
        if usage_percent < CONTEXT_USAGE_SAFE_THRESHOLD:
            return CONTEXT_USAGE_COLORS["safe"]
        elif usage_percent < CONTEXT_USAGE_WARNING_THRESHOLD:
            return CONTEXT_USAGE_COLORS["warning"]
        elif usage_percent < CONTEXT_USAGE_ALERT_THRESHOLD:
            return CONTEXT_USAGE_COLORS["alert"]
        else:
            return CONTEXT_USAGE_COLORS["critical"]
