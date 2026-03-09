"""Professional internationalization (i18n) manager for ExpertGPTs.

Supports 13 languages with automatic system language detection.
"""

import locale
import logging
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from lib.shared.format_ops import read_json

logger = logging.getLogger(__name__)


# Module-level cache for translations (lazy-loaded, reused across instances)
_translations_cache: Dict[str, Dict] = {}


def _get_locales_dir() -> Path:
    """Get the path to the locales directory."""
    return Path(__file__).parent.parent.parent / "locales" / "ui"


def _load_translation(lang_code: str) -> Optional[Dict]:
    """Load a single translation file.

    Args:
        lang_code: Language code to load (e.g., 'en', 'de')

    Returns:
        Translation dictionary or None if not found
    """
    locales_dir = _get_locales_dir()

    if not locales_dir.exists():
        logger.warning(f"Locales directory not found: {locales_dir}")
        return None

    lang_file = locales_dir / f"{lang_code}.json"

    if not lang_file.exists():
        logger.warning(f"Translation file not found: {lang_file}")
        return None

    try:
        data = read_json(lang_file)
        if data is not None:
            logger.debug(f"Loaded translations for {lang_code}")
        return data
    except Exception as e:
        logger.error(f"Error loading {lang_code}: {e}")
        return None


def _ensure_translation_loaded(lang_code: str) -> Optional[Dict]:
    """Ensure a translation is loaded (lazy loading with caching).

    If the translation is already cached, returns cached version.
    Otherwise, loads it from disk and caches it.

    Args:
        lang_code: Language code to ensure is loaded

    Returns:
        Translation dictionary or None if not available
    """
    global _translations_cache

    # Return cached translation if available
    if lang_code in _translations_cache:
        return _translations_cache[lang_code]

    # Load and cache the translation
    data = _load_translation(lang_code)
    if data is not None:
        _translations_cache[lang_code] = data

    return data


def _load_initial_translations() -> Dict[str, Dict]:
    """Load initial translations (English only as fallback).

    English is always loaded as the fallback language.
    Other languages are loaded on-demand when first accessed.

    Returns:
        Dictionary with English translations (and any cached languages)
    """
    # Ensure English is loaded (it's the fallback for all translations)
    _ensure_translation_loaded("en")

    return _translations_cache


# Language metadata with script, direction, and locale info
LANGUAGE_METADATA = {
    "en": {
        "name": "English",
        "native_name": "English",
        "flag": "🇺🇸",
        "script": "Latin",
        "direction": "ltr",
        "locale": "en_US"
    },
    "de": {
        "name": "German",
        "native_name": "Deutsch",
        "flag": "🇩🇪",
        "script": "Latin",
        "direction": "ltr",
        "locale": "de_DE"
    },
    "fr": {
        "name": "French",
        "native_name": "Français",
        "flag": "🇫🇷",
        "script": "Latin",
        "direction": "ltr",
        "locale": "fr_FR"
    },
    "es": {
        "name": "Spanish",
        "native_name": "Español",
        "flag": "🇪🇸",
        "script": "Latin",
        "direction": "ltr",
        "locale": "es_ES"
    },
    "ru": {
        "name": "Russian",
        "native_name": "Русский",
        "flag": "🇷🇺",
        "script": "Cyrillic",
        "direction": "ltr",
        "locale": "ru_RU"
    },
    "it": {
        "name": "Italian",
        "native_name": "Italiano",
        "flag": "🇮🇹",
        "script": "Latin",
        "direction": "ltr",
        "locale": "it_IT"
    },
    "tr": {
        "name": "Turkish",
        "native_name": "Türkçe",
        "flag": "🇹🇷",
        "script": "Latin",
        "direction": "ltr",
        "locale": "tr_TR"
    },
    "pt": {
        "name": "Portuguese",
        "native_name": "Português",
        "flag": "🇵🇹",
        "script": "Latin",
        "direction": "ltr",
        "locale": "pt_PT"
    },
    "id": {
        "name": "Indonesian",
        "native_name": "Bahasa Indonesia",
        "flag": "🇮🇩",
        "script": "Latin",
        "direction": "ltr",
        "locale": "id_ID"
    },
    "ms": {
        "name": "Malay",
        "native_name": "Bahasa Melayu",
        "flag": "🇲🇾",
        "script": "Latin",
        "direction": "ltr",
        "locale": "ms_MY"
    },
    "zh-CN": {
        "name": "Simplified Chinese",
        "native_name": "简体中文",
        "flag": "🇨🇳",
        "script": "Han",
        "direction": "ltr",
        "locale": "zh_CN"
    },
    "zh-TW": {
        "name": "Traditional Chinese",
        "native_name": "繁體中文",
        "flag": "🇹🇼",
        "script": "Han",
        "direction": "ltr",
        "locale": "zh_TW"
    },
    "wyw": {
        "name": "Classical Chinese",
        "native_name": "文言文",
        "flag": "🏛️",
        "script": "Han",
        "direction": "ltr",
        "locale": "wyw"
    },
    "yue": {
        "name": "Cantonese",
        "native_name": "粵語",
        "flag": "🇭🇰",
        "script": "Han",
        "direction": "ltr",
        "locale": "yue"
    },
}


class I18nManager:
    """Professional internationalization manager with RTL and locale support.

    Uses lazy loading for translations - only loads English at startup,
    other languages are loaded on-demand when first accessed.
    """

    def __init__(self):
        # Initialize with English only (other languages loaded on-demand)
        _load_initial_translations()
        self.translations: Dict[str, Dict] = _translations_cache
        self.current_lang: str = "en"

    @property
    def current_language(self) -> str:
        """Get the current language with caching to avoid repeated session state lookups.

        Returns:
            Current language code from session state, or 'en' as default
        """
        if not hasattr(self, '_cached_lang'):
            self._cached_lang = st.session_state.get("language", "en")
        return self._cached_lang

    def invalidate_cache(self):
        """Invalidate the cached language when language changes.

        This should be called whenever the language is changed to ensure
        the cached value is updated.
        """
        if hasattr(self, '_cached_lang'):
            delattr(self, '_cached_lang')

    def detect_system_language(self) -> str:
        """Detect system language and return appropriate language code.

        Returns:
            Language code that matches system language, or 'en' as fallback

        Examples:
            - 'de_DE' → 'de'
            - 'de-AT' → 'de' (Austrian German uses German translation)
            - 'de-CH' → 'de' (Swiss German uses German translation)
            - 'zh_CN' → 'zh-CN'
            - 'fr_FR' → 'fr'
            - 'unsupported' → 'en'
        """
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]

            if not system_locale:
                return "en"

            # Handle special cases first
            # German variants: de-AT (Austrian), de-CH (Swiss), de-DE, de-?? → all use 'de'
            if system_locale.startswith('de'):
                return "de"

            # Chinese variants
            if system_locale in ['zh_CN', 'zh-CN', 'zh_SG']:
                return "zh-CN"
            elif system_locale in ['zh_TW', 'zh-TW', 'zh_HK']:
                return "zh-TW"

            # Extract language code (before '_' or '-')
            lang_code = system_locale.split('_')[0].split('-')[0]

            # Check if we support this language
            if lang_code in LANGUAGE_METADATA:
                return lang_code

            # Fallback to English
            return "en"

        except Exception:
            # If detection fails, use English
            return "en"

    def t(self, key: str, **kwargs) -> str:
        """Get translated string with interpolation.

        Args:
            key: Translation key using dot notation (e.g., "home.title")
            **kwargs: Variables for string interpolation

        Returns:
            Translated string, or key if not found
        """
        lang = self.current_language

        # Ensure the requested language is loaded (lazy loading)
        _ensure_translation_loaded(lang)

        template = self._get_nested(self.translations, lang, key)

        if template is None:
            # Fallback to English if translation not found
            if lang != "en":
                template = self._get_nested(self.translations, "en", key)

            if template is None:
                return key  # Last resort: return the key itself

        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template  # Return template if formatting fails

    def get_language_info(self, code: str) -> Dict:
        """Get comprehensive language metadata."""
        return LANGUAGE_METADATA.get(code, {
            "name": code.upper(),
            "native_name": code.upper(),
            "flag": "🌐",
            "script": "Unknown",
            "direction": "ltr",
            "locale": code
        })

    def get_language_prefix(self, lang: str = None) -> str:
        """Generate language prefix for AI responses.

        Creates a prefix that instructs the AI to respond in the
        user's preferred language, with both English and native
        language names for clarity.

        Args:
            lang: Language code (uses current if None)

        Returns:
            str: Language instruction prefix
            Examples:
                - "You must respond in English."
                - "You must respond in German."
                - "You must respond in French (Français)."
                - "You must respond in Simplified Chinese (简体中文)."
        """
        if lang is None:
            lang = self.current_language

        lang_info = self.get_language_info(lang)
        english_name = lang_info["name"]
        native_name = lang_info["native_name"]

        # Handle special cases for Chinese variants
        if lang == "zh-CN":
            return "You must respond in Simplified Chinese (简体中文)."
        elif lang == "zh-TW":
            return "You must respond in Traditional Chinese (繁體中文)."
        elif english_name == native_name:
            # Language name is same in English and native (e.g., German, Spanish)
            return f"You must respond in {english_name}."
        else:
            # Different names (e.g., French / Français, Italian / Italiano)
            return f"You must respond in {english_name} ({native_name})."

    def get_system_prompt_with_language(self, raw_system_prompt: str) -> str:
        """Inject language prefix into system prompt.

        Args:
            raw_system_prompt: The system prompt from expert configuration

        Returns:
            str: System prompt with language instruction prepended
        """
        language_prefix = self.get_language_prefix()
        return f"{language_prefix}\n\n{raw_system_prompt}"

    def set_language(self, lang: str):
        """Set current language, persist it, and rerun app.

        Args:
            lang: Language code to set (e.g., 'de', 'en')
        """
        if lang in LANGUAGE_METADATA:
            from lib.config.app_defaults_manager import save_language_preference

            # Ensure the new language is loaded (lazy loading)
            _ensure_translation_loaded(lang)

            # Update session state
            st.session_state.language = lang

            # Invalidate cached language
            self.invalidate_cache()

            # Persist to disk
            save_language_preference(lang)

            # Rerun to apply new language
            st.rerun()
        else:
            logger.warning(f"Language '{lang}' not available")

    def _get_nested(self, data: Dict, lang: str, key: str) -> Any:
        """Get nested value from dict using dot notation."""
        if lang not in data:
            return None

        value = data[lang]
        for k in key.split("."):
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value


# Global instance
i18n = I18nManager()
