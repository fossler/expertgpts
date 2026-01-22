"""Utility for managing application default settings.

This module provides functions to read and write application-wide default
settings to the .streamlit/app_defaults.toml file, which persists user
preferences for LLM providers, models, language, and other app defaults.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from lib.shared.file_ops import set_secure_permissions, get_streamlit_path, ensure_file_exists
from lib.shared.constants import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11


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
"""
    return ensure_file_exists(get_app_defaults_path(), default_content=default_content)


def get_llm_defaults() -> Dict[str, Any]:
    """Get current LLM default settings from app_defaults.toml.

    Returns:
        dict: Dictionary with provider, model, and thinking_level defaults
              Returns hardcoded defaults if file doesn't exist or is invalid
    """
    defaults_path = get_app_defaults_path()

    if not defaults_path.exists():
        # Return hardcoded defaults if file doesn't exist
        return {
            "provider": DEFAULT_LLM_PROVIDER,
            "model": DEFAULT_LLM_MODEL,
            "thinking_level": "none"
        }

    try:
        content = defaults_path.read_text()
        data = tomllib.loads(content)

        # Extract LLM defaults, falling back to hardcoded values
        llm_section = data.get("llm", {})

        return {
            "provider": llm_section.get("provider", DEFAULT_LLM_PROVIDER),
            "model": llm_section.get("model", DEFAULT_LLM_MODEL),
            "thinking_level": llm_section.get("thinking_level", "none")
        }
    except Exception as e:
        print(f"Warning: Error reading app_defaults.toml: {e}")
        # Return hardcoded defaults on error
        return {
            "provider": DEFAULT_LLM_PROVIDER,
            "model": DEFAULT_LLM_MODEL,
            "thinking_level": "none"
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

    try:
        # Read existing content to preserve other sections
        try:
            import tomli_w
            # Try to load existing data
            content = defaults_path.read_text()
            data = tomllib.loads(content)
        except Exception:
            # If file is empty or invalid, start fresh
            data = {}

        # Ensure llm section exists
        if "llm" not in data:
            data["llm"] = {}

        # Update LLM defaults
        data["llm"]["provider"] = provider
        data["llm"]["model"] = model
        data["llm"]["thinking_level"] = thinking_level

        # Write back to file using tomli_w
        try:
            import tomli_w
            toml_content = tomli_w.dumps(data)
        except ImportError:
            # Fallback: simple TOML writing for basic cases
            lines = ["# Application Default Settings",
                     "# This file persists your default LLM and other app-wide settings",
                     ""]
            lines.append("[llm]")
            lines.append(f'provider = "{provider}"')
            lines.append(f'model = "{model}"')
            lines.append(f'thinking_level = "{thinking_level}"')
            toml_content = '\n'.join(lines)

        defaults_path.write_text(toml_content)

        # Ensure secure permissions after writing
        set_secure_permissions(defaults_path)

        return True

    except Exception as e:
        print(f"Error saving app_defaults.toml: {e}")
        return False


def has_app_defaults() -> bool:
    """Check if app_defaults.toml file exists.

    Returns:
        bool: True if app_defaults.toml exists, False otherwise
    """
    return get_app_defaults_path().exists()


def reset_app_defaults() -> bool:
    """Reset app defaults to hardcoded values.

    Deletes the app_defaults.toml file if it exists, causing the app
    to fall back to hardcoded defaults on next load.

    Returns:
        bool: True if reset was successful, False otherwise
    """
    defaults_path = get_app_defaults_path()

    try:
        if defaults_path.exists():
            defaults_path.unlink()
        return True
    except Exception as e:
        print(f"Error resetting app defaults: {e}")
        return False


def get_language_preference() -> Optional[str]:
    """Get saved language preference from app_defaults.toml.

    Returns:
        Language code (e.g., 'de', 'en') or None if not set/invalid
    """
    defaults_path = get_app_defaults_path()

    if not defaults_path.exists():
        return None

    try:
        from lib.i18n.i18n import LANGUAGE_METADATA

        content = defaults_path.read_text()
        data = tomllib.loads(content)

        language_section = data.get("language", {})
        lang = language_section.get("code") if isinstance(language_section, dict) else None

        # Validate language is supported
        if lang and lang in LANGUAGE_METADATA:
            return lang

        # Invalid language - return None to trigger auto-detection
        return None
    except Exception:
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

    try:
        # Try to load existing data to preserve other sections
        try:
            content = defaults_path.read_text()
            data = tomllib.loads(content)
        except Exception:
            # If file is empty or invalid, start fresh
            data = {}

        # Update language section
        if "language" not in data:
            data["language"] = {}
        data["language"]["code"] = lang_code

        # Write back to file using tomli_w
        try:
            import tomli_w
            toml_content = tomli_w.dumps(data)
            defaults_path.write_text(toml_content)
        except ImportError:
            # Fallback: simple TOML writing for basic cases
            # Read existing data if possible to preserve llm section
            try:
                content = defaults_path.read_text()
                data = tomllib.loads(content)
            except Exception:
                data = {}

            # Update language
            if "language" not in data:
                data["language"] = {}
            data["language"]["code"] = lang_code

            # Reconstruct file with all sections
            lines = ["# Application Default Settings",
                     "# This file persists your default LLM and other app-wide settings",
                     ""]

            if "llm" in data:
                lines.append("[llm]")
                llm = data["llm"]
                lines.append(f'provider = "{llm.get("provider", DEFAULT_LLM_PROVIDER)}"')
                lines.append(f'model = "{llm.get("model", DEFAULT_LLM_MODEL)}"')
                lines.append(f'thinking_level = "{llm.get("thinking_level", "none")}"')
                lines.append("")

            if "language" in data:
                lines.append("[language]")
                lines.append(f'code = "{data["language"]["code"]}"')

            toml_content = '\n'.join(lines)
            defaults_path.write_text(toml_content)

        # Ensure secure permissions after writing
        set_secure_permissions(defaults_path)

        return True

    except Exception as e:
        print(f"Error saving language preference: {e}")
        return False

