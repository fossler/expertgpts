"""Helper functions for ExpertGPTs."""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import re
import unicodedata


def sanitize_name(name: str) -> str:
    """Sanitize expert name for use in filenames and IDs.

    Converts names to lowercase and replaces spaces and hyphens with underscores.
    Includes security hardening: length limit, Unicode normalization, and empty check.

    Args:
        name: Raw expert name (e.g., "Python Expert", "Data-Scientist")

    Returns:
        Sanitized name (e.g., "python_expert", "data_scientist")

    Raises:
        ValueError: If name is empty or results in empty string after sanitization

    Examples:
        >>> sanitize_name("Python Expert")
        'python_expert'
        >>> sanitize_name("Data-Science Expert")
        'data_science_expert'
        >>> sanitize_name("Career Coach")
        'career_coach'
    """
    if not name or not name.strip():
        raise ValueError("Expert name cannot be empty")

    # Unicode normalization (NFC form) to prevent homograph attacks
    normalized = unicodedata.normalize('NFC', name)

    # Convert to lowercase
    lowercased = normalized.lower()

    # Replace spaces and hyphens with underscores
    sanitized = lowercased.replace(" ", "_").replace("-", "_")

    # Remove any characters that aren't alphanumeric or underscore
    sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)

    # Enforce maximum length (64 characters) to prevent DoS/buffer issues
    MAX_LENGTH = 64
    if len(sanitized) > MAX_LENGTH:
        sanitized = sanitized[:MAX_LENGTH]

    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    # Ensure result is not empty
    if not sanitized:
        raise ValueError("Expert name results in empty string after sanitization")

    return sanitized


def translate_expert_name(expert_name: str) -> str:
    """Translate expert names for default experts.

    Default expert names are stored in English but should be displayed
    in the user's selected language. Custom expert names (user-created)
    are returned as-is.

    This function generates translation keys dynamically using the
    sanitize_name() function, eliminating the need for a duplicate
    mapping dictionary.

    Args:
        expert_name: The expert name from config

    Returns:
        Translated expert name (or original if no translation exists)
    """
    from lib.i18n.i18n import i18n

    # Generate translation key directly from expert name
    sanitized = sanitize_name(expert_name)
    translation_key = f"experts.names.{sanitized}"

    # Attempt to translate, fall back to original if translation fails
    try:
        translated = i18n.t(translation_key)
        # If the translation key itself is returned (no translation), use original
        if translated == translation_key:
            return expert_name
        return translated
    except:
        return expert_name


@st.cache_data(ttl=300, show_spinner=False)
def translate_expert_names_batch(expert_names: tuple, language: str) -> dict:
    """Translate multiple expert names at once (cached).

    This function is optimized for batch translation of expert names
    with 5-minute caching. Use this when rendering expert lists to
    avoid repeated i18n lookups.

    Args:
        expert_names: Tuple of expert names to translate (must be tuple for caching)
        language: Current language code (included in cache key for invalidation)

    Returns:
        Dictionary mapping original names to translated names
    """
    from lib.i18n.i18n import i18n

    return {
        name: _translate_single_name(name, i18n)
        for name in expert_names
    }


def _translate_single_name(expert_name: str, i18n) -> str:
    """Translate a single expert name (internal helper).

    Args:
        expert_name: The expert name to translate
        i18n: I18nManager instance

    Returns:
        Translated name or original if no translation exists
    """
    sanitized = sanitize_name(expert_name)
    translation_key = f"experts.names.{sanitized}"

    try:
        translated = i18n.t(translation_key)
        if translated == translation_key:
            return expert_name
        return translated
    except (KeyError, AttributeError, Exception):
        return expert_name


def validate_expert_name(name: str) -> tuple[bool, str]:
    """Validate expert name contains only allowed characters.

    Allowed characters: A-Z, a-z, 0-9, underscore (_), hyphen (-), dot (.), space ( )

    Args:
        name: The expert name to validate

    Returns:
        tuple: (is_valid, error_message) with i18n support
    """
    from lib.i18n.i18n import i18n

    if not name:
        return False, i18n.t('errors.expert_name_empty')

    # Regex pattern for allowed characters
    pattern = r'^[A-Za-z0-9_.\- ]+$'

    if not re.match(pattern, name):
        allowed = i18n.t('forms.allowed_characters_desc')
        return False, i18n.t('errors.expert_name_invalid_chars', allowed=allowed)

    return True, ""


def validate_api_key(api_key: str, provider: str = None) -> tuple[bool, str]:
    """Validate API key format before using.

    Performs provider-specific validation when provider is specified,
    falling back to generic validation otherwise.

    Args:
        api_key: API key to validate
        provider: Optional provider key for provider-specific validation
                  (e.g., "deepseek", "openai", "zai", "kimi")

    Returns:
        tuple: (is_valid, error_message) with i18n support
        - (True, "") if valid
        - (False, error_message) if invalid
    """
    from lib.i18n.i18n import i18n

    if not api_key:
        return False, i18n.t("errors.api_key_not_set")

    # Provider-specific validation patterns
    PROVIDER_KEY_PATTERNS = {
        "deepseek": {
            "pattern": r"^sk-[a-f0-9]{31,}$",
            "example": "sk-1234567890abcdef1234567890abcdef"
        },
        "openai": {
            "pattern": r"^sk-[a-zA-Z0-9_-]{52,}$",
            "example": "sk-proj-abc123_XyZ789..."
        },
        "zai": {
            "pattern": r"^[a-f0-9]{32}\.[a-zA-Z0-9]{16}$",
            "example": "ab3e366bed0b468586b2bd9e7eab347a.XyZ1234567890AbC"
        },
        "kimi": {
            "pattern": r"^sk-[a-zA-Z0-9]{46,}$",
            "example": "sk-AbCdEf123456XyZ7890GhIjKlMnOpQrStUv"
        }
    }

    # Provider-specific validation
    if provider and provider in PROVIDER_KEY_PATTERNS:
        config = PROVIDER_KEY_PATTERNS[provider]
        if not re.match(config["pattern"], api_key):
            return False, i18n.t("errors.api_key_invalid_format", example=config["example"])
        return True, ""

    # Generic validation (minimum length check)
    if len(api_key) < 20:
        return False, i18n.t("errors.api_key_invalid")

    return True, ""


def sanitize_error_message(message: str) -> str:
    """Sanitize error message to remove sensitive data like API keys.

    Removes any strings that match API key patterns to prevent
    accidental exposure of credentials in logs or UI.

    Args:
        message: Error message that may contain sensitive data

    Returns:
        Sanitized message with API keys replaced by [REDACTED]

    Example:
        >>> sanitize_error_message("Error with key sk-abc123xyz456")
        'Error with key [REDACTED]'
    """
    if not message:
        return message

    sanitized = message

    # API key patterns to redact (order matters - more specific first)
    API_KEY_PATTERNS = [
        # Z.AI format: 32 hex chars + dot + 16 alphanumeric
        (r'[a-f0-9]{32}\.[a-zA-Z0-9]{16}', '[REDACTED]'),
        # DeepSeek format: sk- + 32+ hex chars
        (r'sk-[a-f0-9]{32,}', '[REDACTED]'),
        # OpenAI format: sk- + 20+ alphanumeric/underscore/hyphen
        (r'sk-[a-zA-Z0-9_-]{20,}', '[REDACTED]'),
        # KIMI format: sk- + 20+ alphanumeric
        (r'sk-[a-zA-Z0-9]{20,}', '[REDACTED]'),
        # Generic sk- prefix patterns (catches most API keys)
        (r'sk-[a-zA-Z0-9_-]{10,}', '[REDACTED]'),
    ]

    for pattern, replacement in API_KEY_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)

    return sanitized


def sanitize_markdown_content(content: str) -> str:
    """Sanitize markdown content to prevent injection attacks.

    Removes potentially dangerous URL schemes (javascript:, data:, vbscript:)
    from markdown links and images. Streamlit's st.markdown() already escapes
    HTML by default, but this provides additional protection against malicious
    URLs.

    Args:
        content: Markdown content that may contain malicious constructs

    Returns:
        Sanitized markdown content with dangerous URLs neutralized

    Example:
        >>> sanitize_markdown_content("[click](javascript:alert(1))")
        '[click](about:blank#blocked)'
    """
    if not content:
        return content

    sanitized = content

    # Dangerous URL schemes to block (case-insensitive)
    # Pattern matches: scheme: or scheme:// anything until space or end
    DANGEROUS_SCHEMES = [
        r'javascript\s*:',
        r'vbscript\s*:',
        r'data\s*:',
        r'file\s*:',
    ]

    # Replace dangerous schemes in markdown links and images
    # Pattern: [text](url) or ![alt](url)
    for scheme in DANGEROUS_SCHEMES:
        # Match in markdown link context: ](scheme:...)
        sanitized = re.sub(
            rf'\]\s*\(\s*({scheme})',
            '](about:blank#blocked)',
            sanitized,
            flags=re.IGNORECASE
        )

    return sanitized


def add_error_to_history(
    expert_id: str,
    messages_key: str,
    error_msg: str
) -> None:
    """Add error message to chat history and persist to file.

    This helper centralizes the error persistence pattern used across
    exception handlers, reducing code duplication.

    Args:
        expert_id: Expert identifier (e.g., "1001_python_expert")
        messages_key: Session state key for messages (e.g., "messages_1001_python_expert")
        error_msg: Error message to add (should already be translated/sanitized)
    """
    from lib.storage import save_chat_history

    st.session_state[messages_key].append({
        "role": "assistant",
        "content": f"❌ {error_msg}"
    })
    save_chat_history(expert_id, st.session_state[messages_key])


def get_git_branch() -> str | None:
    """Get the current Git branch name if in a Git repository.

    Returns:
        str | None: Branch name if in a Git repo, None otherwise
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def render_git_branch_footer() -> None:
    """Render Git branch display at the bottom of sidebar.

    Shows the current Git branch if the app is running from a Git repository
    and the display setting is enabled.
    Should be called at the end of sidebar content rendering.
    """
    from lib.config.app_defaults_manager import get_display_defaults

    # Check if Git branch display is enabled
    display_settings = get_display_defaults()
    if not display_settings.get("git_branch", True):
        return

    git_branch = get_git_branch()
    if git_branch:
        st.sidebar.divider()
        st.sidebar.caption(f"🌿 `{git_branch}`")
