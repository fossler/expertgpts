"""Token counting and context usage management for DeepSeek API.

This module provides centralized token management functionality including
counting, caching, and usage statistics calculation.
"""

import streamlit as st
import tiktoken
from lib.shared.constants import (
    DEEPSEEK_MAX_CONTEXT_TOKENS,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS,
)


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

