"""Helper functions for ExpertGPTs."""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import re


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


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate API key format before using.

    Args:
        api_key: API key to validate

    Returns:
        tuple: (is_valid, error_message) with i18n support
        - (True, "") if valid
        - (False, error_message) if invalid
    """
    from lib.i18n.i18n import i18n

    if not api_key:
        return False, i18n.t("errors.api_key_not_set")

    if len(api_key) < 20:
        return False, i18n.t("errors.api_key_invalid")

    # Generic validation - different providers have different formats
    return True, ""
