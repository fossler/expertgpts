"""Tests for i18n infrastructure.

This test suite verifies the i18n architectural implementation:
1. Language prefix generation for all supported languages
2. System prompt construction with language prefix
3. Locale files don't contain expert content
4. YAML configs contain expert content
5. Integration workflow (end-to-end)
"""

import json
import pytest
from pathlib import Path

from lib.i18n import I18nManager
from lib.config import ConfigManager
from lib.shared.format_ops import read_json


class TestI18nLanguagePrefix:
    """Test language prefix generation for all supported languages."""

    @pytest.fixture
    def i18n(self):
        """Get I18nManager instance."""
        return I18nManager()

    @pytest.mark.parametrize("language_code,language_name,expected_phrase", [
        ('en', 'English', 'You must respond in English.'),
        ('de', 'German', 'You must respond in German (Deutsch).'),
        ('es', 'Spanish', 'You must respond in Spanish (Español).'),
        ('fr', 'French', 'You must respond in French (Français).'),
        ('it', 'Italian', 'You must respond in Italian (Italiano).'),
        ('pt', 'Portuguese', 'You must respond in Portuguese (Português).'),
        ('ru', 'Russian', 'You must respond in Russian (Русский).'),
        ('tr', 'Turkish', 'You must respond in Turkish (Türkçe).'),
        ('id', 'Indonesian', 'You must respond in Indonesian (Bahasa Indonesia).'),
        ('ms', 'Malay', 'You must respond in Malay (Bahasa Melayu).'),
        ('zh-CN', 'Simplified Chinese', 'Simplified Chinese (简体中文)'),
        ('zh-TW', 'Traditional Chinese', 'Traditional Chinese (繁體中文)'),
        ('wyw', 'Classical Chinese', 'Classical Chinese (文言文)'),
        ('yue', 'Cantonese', 'Cantonese (粵語)'),
    ])
    def test_language_prefix_generation(self, i18n, language_code, language_name, expected_phrase):
        """Test that language prefix is generated correctly for each language.

        Args:
            i18n: I18nManager fixture
            language_code: ISO language code
            language_name: Human-readable language name
            expected_phrase: Expected phrase in the language prefix
        """
        prefix = i18n.get_language_prefix(language_code)

        assert expected_phrase in prefix, (
            f"Language prefix for {language_name} ({language_code}) should contain "
            f"'{expected_phrase}', but got: {prefix}"
        )

        # Verify it's a non-empty string
        assert len(prefix) > 0, "Language prefix should not be empty"

    def test_invalid_language_code(self, i18n):
        """Test that invalid language codes are handled gracefully.

        Args:
            i18n: I18nManager fixture
        """
        # Should not raise exception for invalid codes
        prefix = i18n.get_language_prefix('invalid-code')
        assert len(prefix) > 0, "Should return a fallback prefix for invalid codes"


class TestI18nSystemPrompt:
    """Test system prompt construction with language prefix."""

    @pytest.fixture
    def i18n(self):
        """Get I18nManager instance."""
        return I18nManager()

    @pytest.fixture
    def raw_system_prompt(self):
        """Sample system prompt without language prefix."""
        return (
            "You are Python Expert, a domain-specific expert AI assistant.\n\n"
            "Expert in Python programming, software development, debugging, and best practices."
        )

    def test_system_prompt_construction_english(self, i18n, raw_system_prompt):
        """Test system prompt construction with English language prefix.

        Args:
            i18n: I18nManager fixture
            raw_system_prompt: Sample system prompt fixture
        """
        language_code = 'en'
        language_prefix = i18n.get_language_prefix(language_code)
        system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"

        # Verify structure: [prefix], [empty line], [raw prompt]
        lines = system_prompt_with_lang.split('\n')
        assert lines[0] == language_prefix, "Language prefix should be first line"
        assert lines[1] == '', "Second line should be empty separator"
        assert raw_system_prompt in system_prompt_with_lang, "Raw prompt should be included"

    def test_system_prompt_construction_german(self, i18n, raw_system_prompt):
        """Test system prompt construction with German language prefix.

        Args:
            i18n: I18nManager fixture
            raw_system_prompt: Sample system prompt fixture
        """
        language_code = 'de'
        language_prefix = i18n.get_language_prefix(language_code)
        system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"

        # Verify structure
        lines = system_prompt_with_lang.split('\n')
        assert lines[0] == language_prefix, "Language prefix should be first line"
        assert lines[1] == '', "Second line should be empty separator"
        assert raw_system_prompt in system_prompt_with_lang, "Raw prompt should be included"
        # Verify it's German
        assert 'Deutsch' in language_prefix, "German prefix should contain 'Deutsch'"

    def test_system_prompt_length(self, i18n, raw_system_prompt):
        """Test that adding language prefix increases prompt length appropriately.

        Args:
            i18n: I18nManager fixture
            raw_system_prompt: Sample system prompt fixture
        """
        language_prefix = i18n.get_language_prefix('de')
        system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"

        # Combined prompt should be longer than raw prompt
        assert len(system_prompt_with_lang) > len(raw_system_prompt), (
            "Combined prompt should be longer than raw prompt"
        )

        # But not excessively long (prefix + 2 newlines + raw)
        expected_length = len(language_prefix) + 2 + len(raw_system_prompt)
        assert len(system_prompt_with_lang) == expected_length


class TestI18nLocaleFiles:
    """Test that locale files are properly structured (no expert content)."""

    @pytest.fixture
    def locale_dir(self):
        """Get locale directory path."""
        return Path("locales/ui")

    def test_locale_files_exist(self, locale_dir):
        """Test that locale files exist.

        Args:
            locale_dir: Locale directory fixture
        """
        locale_files = list(locale_dir.glob("*.json"))
        assert len(locale_files) > 0, "Should have locale files"
        assert (locale_dir / "en.json").exists(), "Should have English locale (source of truth)"

    def test_locale_files_no_expert_content(self, locale_dir):
        """Test that locale files don't contain expert content.

        According to i18n architecture, expert content (system prompts, descriptions)
        should be in YAML configs, not locale files.

        UI translations for expert names (experts.names) are allowed and expected,
        as they are UI elements, not expert content.

        Args:
            locale_dir: Locale directory fixture
        """
        locale_files = sorted(locale_dir.glob("*.json"))

        for locale_file in locale_files:
            data = read_json(locale_file)
            assert data is not None, f"Could not read {locale_file.name}"

            # Should not have top-level expert content sections
            assert 'expert_names' not in data, (
                f"{locale_file.name} should not have top-level 'expert_names' section - "
                "expert names are translated dynamically via helpers.translate_expert_name()"
            )

            # If 'experts' section exists, it should only contain UI-related keys
            if 'experts' in data:
                experts_section = data['experts']
                allowed_ui_keys = {'management', 'names'}

                # Check for disallowed expert content keys
                disallowed_keys = set(experts_section.keys()) - allowed_ui_keys
                assert len(disallowed_keys) == 0, (
                    f"{locale_file.name} 'experts' section has disallowed keys: "
                    f"{disallowed_keys}. Only UI-related keys ({allowed_ui_keys}) are allowed. "
                    "Expert content (system_prompt, description) belongs in YAML configs."
                )

            # Should have UI sections
            assert len(data) > 0, f"{locale_file.name} should have some translations"


class TestI18nYamlConfigs:
    """Test that YAML configs contain expert content (not locale files)."""

    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create temporary config directory for testing.

        Args:
            tmp_path: pytest's temporary path fixture

        Yields:
            Path to temporary config directory
        """
        config_dir = tmp_path / "configs"
        config_dir.mkdir()
        yield config_dir

    def test_yaml_config_has_expert_content(self, temp_config_dir):
        """Test that YAML configs have expert content.

        According to i18n architecture, expert content (name, description, system prompt)
        should be in YAML configs, not locale files.

        Args:
            temp_config_dir: Temporary config directory fixture
        """
        config_manager = ConfigManager(config_dir=str(temp_config_dir))

        # Create a test expert
        expert_id = config_manager.create_config(
            expert_name="Test Expert",
            description="An expert in testing things.",
            page_number=1,
            temperature=0.7,
        )

        # Load and verify
        config = config_manager.load_config(expert_id)

        assert 'expert_name' in config, "YAML config should have expert_name"
        assert 'description' in config, "YAML config should have description"
        assert 'system_prompt' in config, "YAML config should have system_prompt"

        # Verify content
        assert config['expert_name'] == "Test Expert"
        assert len(config['description']) > 0
        assert len(config['system_prompt']) > 0
        assert "Test Expert" in config['system_prompt']


class TestI18nIntegration:
    """Integration tests for end-to-end i18n workflow."""

    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create temporary config directory for testing.

        Args:
            tmp_path: pytest's temporary path fixture

        Yields:
            Path to temporary config directory
        """
        config_dir = tmp_path / "configs"
        config_dir.mkdir()
        yield config_dir

    def test_full_workflow_german_user(self, temp_config_dir):
        """Test full i18n workflow: load config, get prefix, construct prompt.

        Simulates a German user using a Python expert.

        Workflow:
        1. Load expert from YAML config
        2. Get user's language preference
        3. Generate language prefix
        4. Construct system prompt with prefix
        5. Verify it's ready to send to API

        Args:
            temp_config_dir: Temporary config directory fixture
        """
        i18n = I18nManager()
        config_manager = ConfigManager(config_dir=str(temp_config_dir))

        # Step 1: Load expert from YAML config
        expert_id = config_manager.create_config(
            expert_name="Python Expert",
            description="Expert in Python programming and software development.",
            page_number=1,
            temperature=0.7,
        )
        config = config_manager.load_config(expert_id)
        raw_prompt = config.get('system_prompt', '')

        assert config['expert_name'] == "Python Expert"
        assert len(raw_prompt) > 0

        # Step 2: Simulate user's language preference (from app_defaults.toml)
        language_code = 'de'

        # Step 3: Generate language prefix
        language_prefix = i18n.get_language_prefix(language_code)

        assert 'Deutsch' in language_prefix, "German prefix should contain 'Deutsch'"
        assert len(language_prefix) > 0, "Language prefix should not be empty"

        # Step 4: Construct system prompt for API call
        final_prompt = f"{language_prefix}\n\n{raw_prompt}"

        # Step 5: Verify structure
        lines = final_prompt.split('\n')
        assert lines[0].startswith("You must respond in"), (
            "First line should be language instruction"
        )
        assert lines[1] == '', "Second line should be empty separator"
        assert raw_prompt in final_prompt, "Raw prompt should be included"

        # Verify it's ready for API
        assert len(final_prompt) > 100, "Final prompt should have substantial content"
        assert 'Python Expert' in final_prompt, "Expert name should be in prompt"

    def test_full_workflow_chinese_user(self, temp_config_dir):
        """Test full i18n workflow for Chinese user.

        Simulates a Simplified Chinese user using a Data Scientist expert.

        Args:
            temp_config_dir: Temporary config directory fixture
        """
        i18n = I18nManager()
        config_manager = ConfigManager(config_dir=str(temp_config_dir))

        # Create expert
        expert_id = config_manager.create_config(
            expert_name="Data Scientist",
            description="Expert in data analysis, machine learning, and statistics.",
            page_number=1,
            temperature=0.8,
        )
        config = config_manager.load_config(expert_id)
        raw_prompt = config.get('system_prompt', '')

        # Chinese language preference
        language_code = 'zh-CN'
        language_prefix = i18n.get_language_prefix(language_code)

        # Verify Chinese prefix
        assert '简体中文' in language_prefix, "Should contain Simplified Chinese characters"

        # Construct and verify
        final_prompt = f"{language_prefix}\n\n{raw_prompt}"
        assert 'Data Scientist' in final_prompt
        assert 'You must respond in' in final_prompt

    def test_language_switching_doesnt_affect_configs(self, temp_config_dir):
        """Test that changing language doesn't modify YAML configs.

        This verifies the separation of concerns: locale files for UI,
        YAML configs for expert content.

        Args:
            temp_config_dir: Temporary config directory fixture
        """
        i18n = I18nManager()
        config_manager = ConfigManager(config_dir=str(temp_config_dir))

        # Create expert
        expert_id = config_manager.create_config(
            expert_name="Test Expert",
            description="Test description.",
            page_number=1,
            temperature=0.7,
        )

        # Load config once
        config_english = config_manager.load_config(expert_id)
        original_prompt = config_english['system_prompt']

        # Simulate language switch
        _ = i18n.get_language_prefix('de')
        _ = i18n.get_language_prefix('zh-CN')
        _ = i18n.get_language_prefix('es')

        # Load config again - should be unchanged
        config_after = config_manager.load_config(expert_id)

        assert config_after['system_prompt'] == original_prompt, (
            "YAML config should not be affected by language switching"
        )
        assert config_after['expert_name'] == "Test Expert"
        assert config_after['description'] == "Test description."
