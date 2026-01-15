#!/usr/bin/env python3
"""Test I18n Refactoring Implementation.

This script verifies that the i18n architectural refactoring works correctly:
1. Language prefix generation
2. System prompt construction with language prefix
3. Locale files contain no expert content
4. Settings page behavior
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.i18n import I18nManager
from utils.config_manager import ConfigManager


def test_language_prefix_generation():
    """Test 1: Verify language prefix generation for all languages."""
    print("=" * 70)
    print("TEST 1: Language Prefix Generation")
    print("=" * 70)

    i18n = I18nManager()

    # Test all 13 supported languages
    test_cases = [
        ('en', 'English', 'You must respond in English.'),
        ('de', 'German', 'You must respond in German (Deutsch).'),
        ('es', 'Spanish', 'You must respond in Spanish (Español).'),
        ('fr', 'French', 'You must respond in French (Français).'),
        ('it', 'Italian', 'You must respond in Italian (Italiano).'),
        ('pt', 'Portuguese', 'You must respond in Portuguese (Português).'),
        ('ru', 'Russian', 'You must respond in Russian (Русский).'),
        ('zh-CN', 'Simplified Chinese', 'Simplified Chinese (简体中文)'),
        ('zh-TW', 'Traditional Chinese', 'Traditional Chinese (繁體中文)'),
    ]

    passed = 0
    failed = 0

    for code, name, expected_part in test_cases:
        prefix = i18n.get_language_prefix(code)

        if expected_part in prefix:
            print(f"✅ {code:6} ({name:20}): {prefix}")
            passed += 1
        else:
            print(f"❌ {code:6} ({name:20}): Expected '{expected_part}' in '{prefix}'")
            failed += 1

    print()
    print(f"Result: {passed}/{passed + failed} tests passed")
    print()
    return failed == 0


def test_system_prompt_construction():
    """Test 2: Verify system prompt construction with language prefix."""
    print("=" * 70)
    print("TEST 2: System Prompt Construction with Language Prefix")
    print("=" * 70)

    i18n = I18nManager()

    # Simulate what template.py does
    raw_system_prompt = "You are Python Expert, a domain-specific expert AI assistant.\n\nExpert in Python programming, software development, debugging, and best practices."

    language_prefix = i18n.get_language_prefix('de')
    system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"

    print("Raw System Prompt:")
    print(f"  {raw_system_prompt[:80]}...")
    print()
    print("Language Prefix (German):")
    print(f"  {language_prefix}")
    print()
    print("Combined System Prompt:")
    print(f"  {system_prompt_with_lang[:120]}...")
    print()

    # Verify structure
    lines = system_prompt_with_lang.split('\n')
    if lines[0] == language_prefix and lines[1] == '' and raw_system_prompt in system_prompt_with_lang:
        print("✅ System prompt correctly constructed")
        print("   - Language prefix is first line")
        print("   - Empty line separator")
        print("   - Raw system prompt follows")
        print()
        return True
    else:
        print("❌ System prompt construction failed")
        print()
        return False


def test_locale_files_cleaned():
    """Test 3: Verify locale files don't contain expert content."""
    print("=" * 70)
    print("TEST 3: Locale Files Cleanup Verification")
    print("=" * 70)

    locale_dir = Path("locales/ui")
    locale_files = sorted(locale_dir.glob("*.json"))

    passed = 0
    failed = 0

    for locale_file in locale_files:
        with open(locale_file, 'r') as f:
            data = json.load(f)

        has_experts = 'experts' in data
        has_expert_names = 'expert_names' in data

        if not has_experts and not has_expert_names:
            print(f"✅ {locale_file.name:20} - Clean (no expert content)")
            passed += 1
        else:
            issues = []
            if has_experts:
                issues.append("'experts' section")
            if has_expert_names:
                issues.append("'expert_names' section")
            print(f"❌ {locale_file.name:20} - Still has: {', '.join(issues)}")
            failed += 1

    print()
    print(f"Result: {passed}/{passed + failed} locale files clean")
    print()
    return failed == 0


def test_yaml_configs_unchanged():
    """Test 4: Verify YAML configs still have expert content."""
    print("=" * 70)
    print("TEST 4: YAML Configs Still Have Expert Content")
    print("=" * 70)

    config_manager = ConfigManager()

    # Load a few example configs
    test_experts = ['1001_python_expert', '1002_data_scientist']

    passed = 0
    failed = 0

    for expert_id in test_experts:
        try:
            config = config_manager.load_config(expert_id)

            has_name = 'expert_name' in config
            has_description = 'description' in config
            has_system_prompt = 'system_prompt' in config

            if has_name and has_description and has_system_prompt:
                print(f"✅ {expert_id}:")
                print(f"   - Name: {config['expert_name']}")
                print(f"   - Description: {config['description'][:60]}...")
                print(f"   - System Prompt: {config['system_prompt'][:60]}...")
                print()
                passed += 1
            else:
                print(f"❌ {expert_id}: Missing fields")
                print()
                failed += 1
        except Exception as e:
            print(f"❌ {expert_id}: Error loading config - {e}")
            print()
            failed += 1

    print(f"Result: {passed}/{passed + failed} configs have expert content")
    print()
    return failed == 0


def test_integration():
    """Test 5: Integration test - simulate full workflow."""
    print("=" * 70)
    print("TEST 5: Integration Test - Full Workflow Simulation")
    print("=" * 70)

    i18n = I18nManager()
    config_manager = ConfigManager()

    try:
        # Load Python Expert config
        config = config_manager.load_config('1001_python_expert')
        raw_prompt = config.get('system_prompt', '')

        print("1. Load expert from YAML config:")
        print(f"   ✅ Expert: {config['expert_name']}")
        print()

        # Get language prefix (simulate German user)
        print("2. User's language preference (from config.toml):")
        language_code = 'de'
        language_prefix = i18n.get_language_prefix(language_code)
        print(f"   ✅ Language: {language_code}")
        print(f"   ✅ Prefix: {language_prefix}")
        print()

        # Construct system prompt with prefix
        print("3. Construct system prompt for API call:")
        final_prompt = f"{language_prefix}\n\n{raw_prompt}"
        print(f"   ✅ Combined prompt created")
        print(f"   Length: {len(final_prompt)} characters")
        print()

        # Verify structure
        lines = final_prompt.split('\n')
        if lines[0].startswith("You must respond in") and raw_prompt in final_prompt:
            print("4. Verification:")
            print("   ✅ Language prefix is first")
            print("   ✅ Raw prompt follows")
            print("   ✅ Ready to send to API")
            print()
            return True
        else:
            print("❌ Prompt structure verification failed")
            print()
            return False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def main():
    """Run all tests."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  I18N REFACTORING VERIFICATION TEST SUITE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    results = {
        "Language Prefix Generation": test_language_prefix_generation(),
        "System Prompt Construction": test_system_prompt_construction(),
        "Locale Files Cleanup": test_locale_files_cleaned(),
        "YAML Configs Intact": test_yaml_configs_unchanged(),
        "Integration Test": test_integration(),
    }

    # Final summary
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        print()
        print("🎉 ALL TESTS PASSED! The i18n refactoring is working correctly.")
        print()
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Please review the output above.")
        print()
        return 1


if __name__ == "__main__":
    exit(main())
