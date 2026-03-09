"""Utility for managing application default settings.

This module provides functions to read and write application-wide default
settings to the .streamlit/app_defaults.toml file, which persists user
preferences for LLM providers, models, language, and other app defaults.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from lib.shared.file_ops import get_streamlit_path, ensure_streamlit_file
from lib.shared.format_ops import read_toml, write_toml
from lib.shared.constants import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL


def get_app_defaults_path() -> Path:
    """Get the path to the app_defaults.toml file.

    Returns:
        Path: Path to .streamlit/app_defaults.toml in project root
    """
    return get_streamlit_path("app_defaults.toml")


def ensure_app_defaults_file_exists() -> Path:
    """Ensure the .streamlit directory and app_defaults.toml file exist.

    Creates the .streamlit directory and app_defaults.toml file if they don't exist.

    Returns:
        Path: Path to app_defaults.toml file
    """
    default_content = f"""# Application Default Settings
# This file persists your default LLM and other app-wide settings

[llm]
# Default LLM provider (deepseek, openai, zai)
provider = "{DEFAULT_LLM_PROVIDER}"

# Default model for the provider
model = "{DEFAULT_LLM_MODEL}"

# Default thinking/reasoning level for OpenAI models (none, low, medium, high, xhigh)
thinking_level = "none"

[language]
# Default interface language
# Options: en, de, es, fr, it, pt, ru, tr, id, ms, zh-CN, zh-TW, wyw, yue
code = "en"

[display]
# Show Git branch in sidebar footer
git_branch = true
"""
    return ensure_streamlit_file("app_defaults.toml", default_content=default_content)


def get_llm_defaults() -> Dict[str, Any]:
    """Get current LLM default settings from app_defaults.toml.

    Returns:
        dict: Dictionary with provider, model, and thinking_level defaults
              Returns hardcoded defaults if file doesn't exist or is invalid
    """
    defaults_path = get_app_defaults_path()

    # Use shared read_toml function (handles errors, returns {} if missing)
    data = read_toml(defaults_path)

    # Extract LLM defaults, falling back to hardcoded values
    llm_section = data.get("llm", {})

    return {
        "provider": llm_section.get("provider", DEFAULT_LLM_PROVIDER),
        "model": llm_section.get("model", DEFAULT_LLM_MODEL),
        "thinking_level": llm_section.get("thinking_level", "none")
    }


def save_llm_defaults(provider: str, model: str, thinking_level: str) -> bool:
    """Save LLM default settings to app_defaults.toml.

    Args:
        provider: Default LLM provider (e.g., "deepseek", "openai", "zai")
        model: Default model for the provider (e.g., "deepseek-chat", "gpt-5")
        thinking_level: Default thinking level for OpenAI (e.g., "none", "low", "medium")

    Returns:
        bool: True if save was successful, False otherwise
    """
    defaults_path = get_app_defaults_path()

    # Ensure file exists first
    ensure_app_defaults_file_exists()

    # Read existing data to preserve other sections (using shared function)
    data = read_toml(defaults_path)

    # Ensure llm section exists
    if "llm" not in data:
        data["llm"] = {}

    # Update LLM defaults
    data["llm"]["provider"] = provider
    data["llm"]["model"] = model
    data["llm"]["thinking_level"] = thinking_level

    # Write using shared function (handles permissions and errors)
    header = "# Application Default Settings\n# This file persists your default LLM and other app-wide settings\n"
    return write_toml(defaults_path, data, header=header)


def get_language_preference() -> Optional[str]:
    """Get saved language preference from app_defaults.toml.

    Returns:
        Language code (e.g., 'de', 'en') or None if not set/invalid
    """
    from lib.i18n.i18n import LANGUAGE_METADATA

    defaults_path = get_app_defaults_path()

    # Use shared read_toml function (handles errors, returns {} if missing)
    data = read_toml(defaults_path)

    language_section = data.get("language", {})
    lang = language_section.get("code") if isinstance(language_section, dict) else None

    # Validate language is supported
    if lang and lang in LANGUAGE_METADATA:
        return lang

    # Invalid language - return None to trigger auto-detection
    return None


def save_language_preference(lang_code: str) -> bool:
    """Save language preference to app_defaults.toml.

    Args:
        lang_code: Language code to save (e.g., 'de', 'en')

    Returns:
        bool: True if save was successful, False otherwise
    """
    defaults_path = get_app_defaults_path()

    # Ensure file exists first
    ensure_app_defaults_file_exists()

    # Read existing data to preserve other sections (using shared function)
    data = read_toml(defaults_path)

    # Update language section
    if "language" not in data:
        data["language"] = {}
    data["language"]["code"] = lang_code

    # Write using shared function (handles permissions and errors)
    header = "# Application Default Settings\n# This file persists your default LLM and other app-wide settings\n"
    return write_toml(defaults_path, data, header=header)


def get_display_defaults() -> Dict[str, Any]:
    """Get current display settings from app_defaults.toml.

    Returns:
        dict: Dictionary with display settings (e.g., git_branch)
              Returns hardcoded defaults if file doesn't exist or is invalid
    """
    defaults_path = get_app_defaults_path()

    # Use shared read_toml function (handles errors, returns {} if missing)
    data = read_toml(defaults_path)

    # Extract display defaults, falling back to hardcoded values
    display_section = data.get("display", {})

    return {
        "git_branch": display_section.get("git_branch", True)
    }


def save_display_setting(key: str, value: Any) -> bool:
    """Save a display setting to app_defaults.toml.

    Args:
        key: Setting key (e.g., "git_branch")
        value: Setting value

    Returns:
        bool: True if save was successful, False otherwise
    """
    defaults_path = get_app_defaults_path()

    # Ensure file exists first
    ensure_app_defaults_file_exists()

    # Read existing data to preserve other sections (using shared function)
    data = read_toml(defaults_path)

    # Update display section
    if "display" not in data:
        data["display"] = {}
    data["display"][key] = value

    # Write using shared function (handles permissions and errors)
    header = "# Application Default Settings\n# This file persists your default LLM and other app-wide settings\n"
    return write_toml(defaults_path, data, header=header)

