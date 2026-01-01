"""Application-wide constants for ExpertGPTs.

This module centralizes all magic numbers, thresholds, and configuration
values used throughout the application.
"""

# DeepSeek API Constants
DEEPSEEK_MAX_CONTEXT_TOKENS = 128000
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 1.0

# Context Usage Thresholds (percentages)
CONTEXT_USAGE_SAFE_THRESHOLD = 50
CONTEXT_USAGE_WARNING_THRESHOLD = 75
CONTEXT_USAGE_ALERT_THRESHOLD = 90

# Context Usage Colors (emojis for UI display)
CONTEXT_USAGE_COLORS = {
    "safe": "🟢",
    "warning": "🟡",
    "alert": "🟠",
    "critical": "🔴"
}

# Cache TTLs (seconds)
CONFIG_CACHE_TTL = 300
TOKEN_COUNT_CACHE_TTL = 60
SYSTEM_PROMPT_CACHE_TTL = 300
