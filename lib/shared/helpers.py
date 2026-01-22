"""Helper functions for ExpertGPTs."""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from lib.i18n.i18n import i18n


def sanitize_name(name: str) -> str:
    """Sanitize expert name for use in filenames and IDs.

    Converts names to lowercase and replaces spaces and hyphens with underscores.

    Args:
        name: Raw expert name (e.g., "Python Expert", "Data-Scientist")

    Returns:
        Sanitized name (e.g., "python_expert", "data_scientist")

    Examples:
        >>> sanitize_name("Python Expert")
        'python_expert'
        >>> sanitize_name("Data-Science Expert")
        'data_science_expert'
        >>> sanitize_name("Career Coach")
        'career_coach'
    """
    return name.lower().replace(" ", "_").replace("-", "_")


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
