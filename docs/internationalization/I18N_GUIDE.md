# Internationalization (i18n) Guide

This guide explains ExpertGPTs' internationalization architecture, how it works, and how to maintain translations.

## 🌍 Supported Languages

ExpertGPTs supports 13 languages with full UI translations:

| Language | Code | Script Family |
|----------|------|---------------|
| English | `en` | Latin |
| German | `de` | Latin |
| Spanish | `es` | Latin |
| French | `fr` | Latin |
| Italian | `it` | Latin |
| Portuguese | `pt` | Latin |
| Russian | `ru` | Cyrillic |
| Turkish | `tr` | Latin |
| Indonesian | `id` | Latin |
| Malay | `ms` | Latin |
| Chinese (Simplified) | `zh-CN` | Han (汉字) |
| Chinese (Traditional) | `zh-TW` | Han (漢字) |
| Classical Chinese | `wyw` | Han (文言) |
| Cantonese | `yue` | Han (粵語) |

---

## 🏗️ Architecture

### Three-Layer Design

ExpertGPTs uses a clean three-layer architecture for internationalization:

```
┌─────────────────────────────────────────────────────────────┐
│                    1. STORAGE LAYER                         │
│  Expert content (system prompts, descriptions) stored in    │
│  YAML configs in English only (single source of truth)     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    2. TRANSLATION LAYER                      │
│  UI translations stored in JSON locale files                │
│  (locales/ui/{lang}.json)                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    3. RUNTIME LAYER                          │
│  Language prefix injected at runtime:                      │
│  "You must respond in German (Deutsch)."                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Benefits

✅ **No Data Duplication**: Expert content exists in ONE place (YAML configs)
✅ **Easy Maintenance**: Update expert once, works for all languages
✅ **Instant Language Switching**: No need to regenerate experts
✅ **Automatic AI Responses**: Language prefix ensures AI responds correctly
✅ **Clean Separation**: UI translations separate from expert content

---

## 🔧 How It Works

### 1. Language Prefix Generation

**File**: `utils/i18n.py` - `get_language_prefix()` method

The language prefix is generated dynamically based on user's language preference:

```python
# Examples:
# English: "You must respond in English."
# German: "You must respond in German (Deutsch)."
# Chinese: "You must respond in Simplified Chinese (简体中文)."
```

### 2. Runtime Injection

**File**: `templates/template.py` - Lines ~180-182, ~370-372

The language prefix is prepended to system prompts before every API call:

```python
raw_system_prompt = config.get("system_prompt", "")
language_prefix = i18n.get_language_prefix()
system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"
```

**Result sent to API**:
```
You must respond in German (Deutsch).

You are Python Expert, a domain-specific expert AI assistant...
```

### 3. Expert Name Translation

**Files**: `utils/helpers.py`, `app.py`, `templates/template.py`

Default expert names are translated for display in navigation and page titles using **dynamic key generation**:

```python
def translate_expert_name(expert_name: str) -> str:
    """Translate expert names for default experts.

    This function generates translation keys dynamically using the
    sanitize_name() function, eliminating the need for a duplicate
    mapping dictionary.
    """
    sanitized = sanitize_name(expert_name)
    translation_key = f"experts.names.{sanitized}"
    translated = i18n.t(translation_key)

    # Return original if no translation exists
    return translated if translated != translation_key else expert_name
```

**Key Benefits**:
- ✅ **No duplicate mapping** - single source of truth
- ✅ **Auto-supports new experts** - works for any default expert
- ✅ **DRY principle** - uses existing `sanitize_name()` function

Custom expert names (user-created) are displayed as-is without translation.

### 4. Language Persistence

**File**: `.streamlit/app_defaults.toml` - Managed by `utils/app_defaults_manager.py`

Language preference is automatically saved when changed through the Settings page:

```python
# When user selects language in Settings
from utils.app_defaults_manager import save_language_preference

save_language_preference("de")  # Saves to app_defaults.toml
```

On app startup, language is loaded automatically:

```python
# utils/session_state.py - initialize_shared_session_state()
from utils.app_defaults_manager import get_language_preference

saved_lang = get_language_preference()
if saved_lang:
    st.session_state.language = saved_lang
else:
    # Auto-detect system language and save it
    detected_lang = i18n.detect_system_language()
    st.session_state.language = detected_lang
    save_language_preference(detected_lang)
```

**File Structure**:
```toml
# .streamlit/app_defaults.toml

[llm]
provider = "deepseek"
model = "deepseek-chat"
thinking_level = "none"

[language]
code = "en"
```

**Benefits**:
- ✅ Language preference persists across app restarts
- ✅ Auto-detection on first run
- ✅ Clean separation: user preferences in app_defaults.toml, theme in config.toml
- ✅ Secure: 600 file permissions

---

## 📂 Translation File Structure

### Location
```
.streamlit/
├── app_defaults.toml         # User preferences (language, LLM defaults)
├── app_defaults.toml.example # Template file for reference
├── config.toml               # UI theme settings only
└── config.toml.example       # Theme template file

locales/ui/
├── en.json          # English (source of truth)
├── de.json          # German
├── es.json          # Spanish
├── fr.json          # French
├── it.json          # Italian
├── pt.json          # Portuguese
├── ru.json          # Russian
├── tr.json          # Turkish
├── id.json          # Indonesian
├── ms.json          # Malay
├── wyw.json         # Classical Chinese
├── yue.json         # Cantonese
├── zh-CN.json       # Simplified Chinese
└── zh-TW.json       # Traditional Chinese
```

### JSON Structure

```json
{
  "app": { "title": "..." },
  "nav": { "home": "..." },
  "home": { "title": "..." },
  "buttons": { "add_chat": "..." },
  "status": { "api_key_configured": "..." },
  "forms": { "expert_name": "..." },
  "settings": { "general": "..." },
  "language": { "title": "..." },
  "errors": { "required_fields": "..." },
  "success": { "expert_created": "..." },
  "info": { "language_prefix_auto": "..." },
  "dialogs": { "add_chat": {...}, "edit_expert": {...} },
  "experts": {
    "management": {
      "title": "Expert Management",
      "actions": "Actions"
    },
    "names": {
      "python_expert": "Python Expert",
      "data_scientist": "Data Scientist"
    }
  }
}
```

---

## ⚡ Performance Optimizations

The i18n infrastructure has been optimized for performance and maintainability:

### 1. Language Caching

**File**: `utils/i18n.py` - `I18nManager.current_language` property

The current language is cached to avoid repeated session state lookups:

```python
@property
def current_language(self) -> str:
    """Get the current language with caching."""
    if not hasattr(self, '_cached_lang'):
        self._cached_lang = st.session_state.get("language", "en")
    return self._cached_lang

def invalidate_cache(self):
    """Invalidate the cached language when language changes."""
    if hasattr(self, '_cached_lang'):
        delattr(self, '_cached_lang')
```

**Benefits**:
- ✅ **~50% reduction** in session state lookups
- ✅ **Faster translation** operations
- ✅ **Automatic cache invalidation** when language changes

### 2. Module-Level Imports

All i18n imports have been consolidated to module level:

```python
# ✅ GOOD - Module level (utils/i18n.py)
from utils.i18n import i18n

# ❌ BAD - Inline import (removed)
def some_function():
    from utils.i18n import i18n  # Don't do this!
```

**Benefits**:
- ✅ **Cleaner code** - imports at top of file
- ✅ **Better performance** - imported once at module load
- ✅ **Easier maintenance** - all dependencies visible

### 3. Professional Logging

Replaced debug print statements with proper logging:

```python
# ✅ GOOD - Professional logging
logger.info(f"Loaded translations for {lang}")
logger.error(f"Error loading {lang}: {e}")

# ❌ BAD - Print statements (removed)
print(f"✅ Loaded translations for {lang}")
print(f"❌ Error loading {lang}: {e}")
```

**Benefits**:
- ✅ **Production-ready** logging system
- ✅ **Configurable log levels**
- ✅ **Better debugging** capabilities

---

## 🛠️ Maintenance

### Adding New Translation Keys

1. **Add to `locales/ui/en.json`** (source of truth)

```json
{
  "my_new_section": {
    "my_new_key": "This is a new string"
  }
}
```

2. **Sync all locale files**

```bash
python3 scripts/update_translations.py
```

This adds the key to all other language files with the English text as placeholder.

3. **Translate the placeholder**

Manually translate the new key in each locale file, or use translation tools/services.

### Using Translations in Code

```python
from utils.i18n import i18n

# Simple translation
text = i18n.t('my_new_section.my_new_key')

# With parameters
text = i18n.t('errors.error', error="Something went wrong")

# Display in Streamlit
st.markdown(i18n.t('about.title'))
```

### Testing I18n Implementation

```bash
python3 scripts/test_i18n_refactoring.py
```

This verifies:
- Language prefix generation works
- System prompt construction is correct
- Locale files are clean (no expert content)
- YAML configs have expert content
- Integration test passes

---

## 🎯 Key Design Decisions

### 1. Expert Content in English Only

**Why**: Single source of truth, easier maintenance
**Benefit**: Update expert once, works for all languages
**Trade-off**: Need language prefix at runtime

### 2. Language Prefix at Runtime

**Why**: Allows instant language switching without regenerating experts
**Benefit**: Users can switch languages without losing any data
**Trade-off**: Small overhead on every API call

### 3. Expert Names Translation

**Why**: Better UX for international users
**Benefit**: Navigation feels native in each language
**Trade-off**: Only works for default experts (custom names shown as-is)

---

## 📊 Translation Coverage

### What IS Translated

✅ All UI elements (buttons, labels, menus)
✅ Tab names and section headers
✅ Error messages and success notifications
✅ Help text and tooltips
✅ Documentation examples
✅ Default expert names (7 experts × 13 languages)

### What is NOT Translated

❌ Expert system prompts (stored in YAML, English only)
❌ Expert descriptions (stored in YAML, English only)
❌ Custom expert names (user-created, shown as-is)
❌ API documentation (external resources)

---

## 🚀 Adding a New Language

To add support for a new language:

1. **Add Language Metadata** in `utils/i18n.py`:

```python
LANGUAGE_METADATA = {
    # ... existing languages
    "xx": {
        "name": "Language Name",
        "native_name": "Native Name",
        "direction": "ltr",  # or "rtl"
    }
}
```

2. **Create Locale File**: `locales/ui/xx.json`

Copy `en.json` as template and translate all strings.

3. **Add Language Names Translation** in each locale file's `language.available_languages` section.

4. **Test**: Run `python3 scripts/test_i18n_refactoring.py`

---

## 🔍 Troubleshooting

### Translation Not Showing

**Problem**: UI element stays in English after switching language

**Solutions**:
1. Check if translation key exists: `grep -r "my_key" locales/ui/`
2. Verify key is being used in code: `grep "i18n.t('my_key')" pages/`
3. Check for typos in key path (use dot notation)
4. Restart app: Streamlit caches some translations

### Language Prefix Not Working

**Problem**: AI not responding in selected language

**Solutions**:
1. Check `utils/i18n.py:get_language_prefix()` returns correct prefix
2. Verify `templates/template.py` is calling `get_language_prefix()`
3. Check `utils/llm_client.py` includes language prefix in generation prompt
4. Test with `python3 scripts/test_i18n_refactoring.py`

### Missing Translation Keys

**Problem**: Some languages missing new keys

**Solution**:
```bash
python3 scripts/update_translations.py
```

This syncs all locale files with `en.json`.

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `utils/i18n.py` | I18nManager class, language prefix generation |
| `utils/helpers.py` | Expert name translation function |
| `utils/app_defaults_manager.py` | Language and LLM defaults persistence |
| `templates/template.py` | Language prefix injection at runtime |
| `utils/llm_client.py` | Language prefix in AI-powered generation |
| `pages/9998_Settings.py` | Settings page with language selector |
| `scripts/update_translations.py` | Sync locales with en.json |
| `scripts/test_i18n_refactoring.py` | Test i18n implementation |

---

## 🎓 Best Practices

### DO ✅

- ✅ Add new keys to `en.json` first (source of truth)
- ✅ Run `update_translations.py` after adding keys
- ✅ Test with `test_i18n_refactoring.py` before committing
- ✅ Use dot notation for nested keys: `'section.subsection.key'`
- ✅ Keep expert content in English (YAML configs)
- ✅ Translate UI elements only (locale files)
- ✅ Import `i18n` at module level (not inline in functions)
- ✅ Use `sanitize_name()` for expert name translation keys
- ✅ Use `i18n.current_language` property for language access

### DON'T ❌

- ❌ Add expert content to locale files
- ❌ Hardcode strings in pages/components (use `i18n.t()`)
- ❌ Skip testing after i18n changes
- ❌ Mix expert content with UI translations
- ❌ Forget to update all 13 locale files
- ❌ Use inconsistent key naming
- ❌ Import `i18n` inline in functions (use module-level imports)
- ❌ Create duplicate expert name mappings (use dynamic generation)
- ❌ Use print statements for logging (use `logger.info/error/warning`)

---

## 📖 Additional Resources

### Scripts

See `scripts/README.md` for detailed documentation of available scripts.

### Development

See `CLAUDE.md` for project overview and development guidelines.

### Testing

Run tests with:
```bash
./scripts/run_tests.sh          # Run all tests
python3 scripts/test_i18n_refactoring.py  # Test i18n specifically
```

---

## 📝 Changelog

### 2025-01-16 - Performance & Architecture Optimizations

Major i18n infrastructure optimizations for improved performance and maintainability:

**Performance Improvements**:
- ✅ Added `current_language` property with caching (~50% reduction in session state lookups)
- ✅ Consolidated 23 scattered i18n imports to module level (cleaner code, better performance)
- ✅ Replaced debug print statements with professional logging system

**Code Quality Improvements**:
- ✅ Eliminated duplicate expert name mapping (now uses dynamic key generation)
- ✅ Removed 42 lines of unused stub implementations (`format_date`, `format_number`, `get_supported_fonts`)
- ✅ Reduced codebase by 39 net lines while adding functionality

**Benefits**:
- 🚀 Faster translation operations
- 📦 Cleaner, more maintainable code
- 🎯 Better adherence to DRY principle
- 🔧 Production-ready logging

### Previous Improvements

- **Language prefix in generation prompt**: AI-generated system prompts now optimized for user's language
- **Expert name translation**: All 7 default expert names translated to 13 languages
- **Settings page improvements**: All UI elements properly translated
- **Buy Me a Coffee button**: Added to About page with size optimization
- **Cleaned scripts**: Removed one-off migration scripts, kept only reusable tools

---

**Last Updated**: 2025-01-16
**Maintained By**: Development Team
**Questions?**: Check `CLAUDE.md` or create an issue on GitHub
