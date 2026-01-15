"""Helper functions for ExpertGPTs."""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


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

    Args:
        expert_name: The expert name from config

    Returns:
        Translated expert name (or original if no translation exists)
    """
    from utils.i18n import i18n

    # Mapping of default expert names to translation keys
    expert_name_translations = {
        "Python Expert": "experts.names.python_expert",
        "Data Scientist": "experts.names.data_scientist",
        "Writing Assistant": "experts.names.writing_assistant",
        "Linux System Admin": "experts.names.linux_admin",
        "General Assistant": "experts.names.general_assistant",
        "Translation Expert": "experts.names.translation_expert",
        "Spell Checker": "experts.names.spell_checker",
    }

    # Check if this is a default expert that should be translated
    translation_key = expert_name_translations.get(expert_name)

    if translation_key:
        # Attempt to translate, fall back to original if translation fails
        try:
            translated = i18n.t(translation_key)
            # If the translation key itself is returned (no translation), use original
            if translated == translation_key:
                return expert_name
            return translated
        except:
            return expert_name

    # Return original name for custom experts
    return expert_name
