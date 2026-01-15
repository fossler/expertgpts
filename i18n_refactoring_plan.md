# I18n Architectural Refactoring Plan

## Overview

Eliminate data duplication between `configs/*.yaml` and `locales/ui/*.json` by establishing clear separation of concerns:
- **YAML configs**: Store expert content (names, descriptions, system prompts) in English
- **Locale files**: Store ONLY UI translations (buttons, labels, messages)
- **Runtime**: Inject language prefix to ensure AI responds in user's language

---

## Problem Statement

### Current State (DATA DUPLICATION)

**Example: Python Expert content exists in TWO places:**

1. **configs/1001_python_expert.yaml:**
   ```yaml
   expert_name: Python Expert
   description: Expert in Python programming...
   system_prompt: You are Python Expert...
   ```

2. **locales/ui/en.json (and de.json, es.json, etc.):**
   ```json
   {
     "experts": {
       "python_expert": {
         "name": "Python Expert",
         "description": "Expert in Python programming...",
         "system_prompt": "You are Python Expert..."
       }
     }
   }
   ```

**Issues:**
- ❌ Expert content duplicated across 14 files (1 YAML × 13 locale files)
- ❌ Maintenance nightmare: Changes require updating 14 files
- ❌ Violates DRY principle
- ❌ Confusing: Which is the source of truth?

---

## Target Architecture

### Clear Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│  1. STORAGE LAYER (configs/*.yaml)                      │
│                                                         │
│  Expert content in English only:                        │
│  - expert_name (English)                                │
│  - description (English)                                │
│  - system_prompt (English)                              │
│                                                         │
│  Source of truth for expert data                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. TRANSLATION LAYER (locales/ui/*.json)               │
│                                                         │
│  UI translations ONLY:                                  │
│  - Buttons, labels, messages                            │
│  - Navigation, forms, dialogs                           │
│  - Error messages, status messages                      │
│                                                         │
│  NO expert content (names, descriptions, prompts)       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. RUNTIME LAYER (template.py, i18n.py)                │
│                                                         │
│  Language prefix injection:                             │
│  - Read language from config.toml                       │
│  - Generate: "You must respond in {LANGUAGE} ..."       │
│  - Prefix API calls with language instruction           │
│  - Prefix AI-generated system prompts                   │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Add Language Prefix Helper

**File: `utils/i18n.py`**

Add method to generate language prefix:

```python
def get_language_prefix(self, lang: str = None) -> str:
    """Generate language prefix for AI responses.

    Creates a prefix that instructs the AI to respond in the
    user's preferred language, with both English and native
    language names for clarity.

    Args:
        lang: Language code (uses current if None)

    Returns:
        str: Language instruction prefix
        Example: "You must respond in German (Deutsch)."
    """
    if lang is None:
        lang = st.session_state.get("language", "en")

    lang_info = self.get_language_info(lang)
    english_name = lang_info["english_name"]
    native_name = lang_info["native_name"]

    # Handle special cases for Chinese variants
    if lang == "zh-CN":
        return f"You must respond in Simplified Chinese (简体中文)."
    elif lang == "zh-TW":
        return f"You must respond in Traditional Chinese (繁體中文)."
    elif english_name == native_name:
        # Language name is same in English and native (e.g., German)
        return f"You must respond in {english_name}."
    else:
        # Different names (e.g., French / Français)
        return f"You must respond in {english_name} ({native_name})."
```

**Rationale:**
- Clear, unambiguous instruction to AI
- Uses both English and native names for clarity
- Handles special cases (Chinese variants, identical names)

---

### Phase 2: Inject Prefix in Template API Calls

**File: `templates/template.py`**

Find where API calls are made and inject language prefix:

```python
# Current code (around line ~200):
api_messages = [
    {"role": "system", "content": system_prompt},
    *st.session_state[f"messages_{EXPERT_ID}"]
]

# New code:
# Prepare language prefix
language_prefix = i18n.get_language_prefix()

# Prepare system prompt with language prefix
system_prompt_with_lang = f"{language_prefix}\n\n{system_prompt}"

api_messages = [
    {"role": "system", "content": system_prompt_with_lang},
    *st.session_state[f"messages_{EXPERT_ID}"]
]
```

**Benefits:**
- AI now knows to respond in user's language
- Works for both English experts and user-created experts
- No changes to YAML configs needed

---

### Phase 3: Inject Prefix in Auto-Generated System Prompts

**File: `utils/llm_client.py`** (or wherever `generate_system_prompt()` lives)

Update the generation prompt to include language instruction:

```python
def generate_system_prompt(
    self,
    expert_name: str,
    description: str
) -> str:
    """Generate system prompt from expert description using LLM.

    Args:
        expert_name: Name of the expert
        description: Expert description

    Returns:
        Generated system prompt
    """
    from utils.i18n import i18n

    # Get language prefix
    language_prefix = i18n.get_language_prefix()

    # Prepare generation prompt with language instruction
    generation_prompt = f"""{language_prefix}

Generate a system prompt for an AI expert assistant based on the following information:

Expert Name: {expert_name}
Description: {description}

The system prompt should:
1. Be concise (2-3 sentences)
2. Reflect the expert's specialization
4. Be in English (do not translate)

Generate only the system prompt text, nothing else."""

    # Call LLM to generate prompt
    # ... existing generation logic ...
```

**Rationale:**
- Auto-generated prompts will now include language prefix
- AI generates prompt in English, but adds language instruction
- Ensures all experts (default and user-created) respond in user's language

---

### Phase 4: Remove Expert Content from Locale Files

**Files: `locales/ui/*.json` (all 13 languages)**

Remove ALL expert-related keys:

**Keys to remove:**
```json
"experts": { ... },           // ENTIRE SECTION
"expert_names": { ... },      // ENTIRE SECTION
"experts_": { ... }           // If exists
```

**Result:**
- Locale files become smaller and focused on UI only
- No more data duplication
- Clear separation of concerns

**Script to automate:**
```python
import json
from pathlib import Path

locale_dir = Path("locales/ui")
for locale_file in locale_dir.glob("*.json"):
    with open(locale_file, 'r') as f:
        data = json.load(f)

    # Remove expert content
    data.pop("experts", None)
    data.pop("expert_names", None)
    data.pop("experts_", None)

    # Write back
    with open(locale_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned {locale_file.name}")
```

---

### Phase 5: Update i18n Helper Methods

**File: `utils/i18n.py`**

Remove or update methods that relied on locale files for expert content:

**Methods to remove/update:**

1. `get_expert_name()` - Remove (use YAML config instead)
2. `get_expert_description()` - Remove (use YAML config instead)
3. `get_expert_system_prompt()` - Remove or simplify

**New approach:**
```python
# OLD (removed):
def get_expert_name(self, expert_id: str) -> str:
    """Get expert name from locale."""
    # ... translation logic ...

# NEW (not needed - load from YAML directly):
# expert_config = config_manager.load_config(expert_id)
# expert_name = expert_config["expert_name"]
```

---

### Phase 6: Update View/Edit Modes in Settings

**File: `pages/9999_Settings.py`**

**View Mode:**
- Currently uses: `i18n.get_expert_system_prompt(expert_id, raw_prompt)`
- Change to: Use raw prompt from YAML + add language prefix display

```python
# OLD:
translated_prompt = i18n.get_expert_system_prompt(expert_id, raw_prompt)
st.markdown(translated_prompt)

# NEW:
from utils.i18n import i18n
language_prefix = i18n.get_language_prefix()
st.markdown(f"**{language_prefix}**")
st.markdown(raw_prompt)
```

**Edit Mode:**
- Currently shows: Translated prompt for editing
- Change to: Show raw English prompt with note about language prefix

```python
# OLD (with translation):
translated_system_prompt = i18n.get_expert_system_prompt(expert_id, raw_system_prompt)
custom_system_prompt = st.text_area(..., value=translated_system_prompt)

# NEW (raw only):
custom_system_prompt = st.text_area(..., value=raw_system_prompt, help="The expert will automatically respond in the user's selected language.")
```

---

### Phase 7: Verify YAML Configs are in English

**Files: `configs/*.yaml`** (all default experts)

Ensure all 7 default experts have English content:

```yaml
# configs/1001_python_expert.yaml
expert_name: Python Expert          # ✓ Already in English
description: Expert in Python...    # ✓ Already in English
system_prompt: You are Python...    # ✓ Already in English
```

**Verification script:**
```python
import yaml
from pathlib import Path

configs_dir = Path("configs")
for config_file in configs_dir.glob("*.yaml"):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    print(f"✓ {config_file.name}")
    print(f"  Name: {config.get('expert_name')}")
    print(f"  Description: {config.get('description', '')[:50]}...")
```

---

## Migration Steps

### Step 1: Add Language Prefix Helper (No Breaking Changes)
- Add `get_language_prefix()` to `utils/i18n.py`
- Test with all 13 languages
- Verify output format

### Step 2: Inject Prefix in API Calls (Backward Compatible)
- Update `templates/template.py` to add language prefix
- Test: Create Python expert, set language to German, verify AI responds in German
- No changes to configs or locale files yet

### Step 3: Inject Prefix in Prompt Generation
- Update `generate_system_prompt()` to include language instruction
- Test: Create new expert, verify auto-generated prompt includes prefix

### Step 4: Remove Expert Content from Locale Files
- Run automated cleanup script
- Commit changes
- Verify app still works

### Step 5: Update i18n Helper Methods
- Remove `get_expert_name()`, `get_expert_description()`, `get_expert_system_prompt()`
- Update all call sites to use YAML configs directly

### Step 6: Update Settings Page
- Update View mode to show raw prompt + language prefix
- Update Edit mode to edit raw prompt only
- Test View/Edit functionality

### Step 7: Final Testing
- Test all 7 default experts in all 13 languages
- Test creating new experts
- Test editing existing experts
- Verify language persistence works with new architecture

---

## Files to Modify

### Add Language Prefix
1. **`utils/i18n.py`** - Add `get_language_prefix()` method

### Inject Prefix
2. **`templates/template.py`** - Add prefix to API calls
3. **`utils/llm_client.py`** - Add prefix to prompt generation

### Remove Duplication
4. **`locales/ui/*.json`** (13 files) - Remove expert content sections
5. **`utils/i18n.py`** - Remove expert-specific helper methods

### Update UI
6. **`pages/9999_Settings.py`** - Update View/Edit modes

### Verify
7. **`configs/*.yaml`** - Verify English content (no changes needed)

---

## Testing Strategy

### Unit Tests

1. **Language Prefix Generation:**
   ```python
   def test_get_language_prefix():
       i18n = I18nManager()

       # Test English
       assert i18n.get_language_prefix("en") == "You must respond in English."

       # Test German
       assert i18n.get_language_prefix("de") == "You must respond in German."

       # Test French (different native name)
       assert i18n.get_language_prefix("fr") == "You must respond in French (Français)."

       # Test Chinese variants
       assert "Simplified Chinese (简体中文)" in i18n.get_language_prefix("zh-CN")
       assert "Traditional Chinese (繁體中文)" in i18n.get_language_prefix("zh-TW")
   ```

2. **Locale File Cleanup:**
   ```python
   def test_locale_files_no_expert_content():
       for locale_file in Path("locales/ui").glob("*.json"):
           with open(locale_file) as f:
               data = json.load(f)

           # Should not have expert content
           assert "experts" not in data
           assert "expert_names" not in data
   ```

### Integration Tests

1. **Expert Response Language:**
   - Set language to German
   - Chat with Python Expert
   - Verify AI responds in German
   - Repeat for all 13 languages

2. **Expert Creation:**
   - Set language to Spanish
   - Create new expert
   - Verify system prompt includes Spanish prefix
   - Verify AI responds in Spanish

3. **Expert Editing:**
   - Edit existing expert
   - Verify changes saved to YAML
   - Verify language prefix still applied

### Manual Testing Checklist

- [ ] All 7 default experts work in all 13 languages
- [ ] Creating new expert works in any language
- [ ] Editing expert saves to YAML correctly
- [ ] Language preference persists across app restarts
- [ ] Locale files contain NO expert content
- [ ] YAML configs are source of truth
- [ ] No data duplication

---

## Compatibility with Language Persistence Feature

### ✅ Enhances Language Persistence

The new language persistence feature (`.streamlit/config.toml`) makes this refactoring EASIER:

**Before persistence:**
- Language only in `st.session_state` (volatile)
- Had to read system locale on every run
- Inconsistent across sessions

**After persistence:**
- Language saved in `config.toml` (persistent)
- Read once on app startup
- Consistent across sessions
- **Perfect source for language prefix generation**

### Integration Point

```python
# In session_state.py:
if "language" not in st.session_state:
    saved_lang = get_language_preference()  # From config.toml
    if saved_lang:
        st.session_state.language = saved_lang
    else:
        detected_lang = i18n.detect_system_language()
        st.session_state.language = detected_lang
        save_language_preference(detected_lang)

# In template.py (at runtime):
language_prefix = i18n.get_language_prefix()  # Uses st.session_state.language
# Injects: "You must respond in German (Deutsch)."
```

**Benefits:**
- Single source of truth for language preference
- No race conditions between detection and usage
- User's choice always respected
- Auto-detect only on first run

---

## Success Criteria

✅ **No Data Duplication**
- Expert content exists ONLY in YAML configs
- Locale files contain ONLY UI translations

✅ **Language Respect**
- AI responds in user's selected language (all 13 languages)
- Language prefix works for default and user-created experts

✅ **Backward Compatibility**
- Existing experts continue working
- No breaking changes for users

✅ **Maintenance**
- Single source of truth (YAML configs)
- Changing expert content requires updating 1 file, not 14

✅ **User Experience**
- Language preference persists (already implemented)
- Expert creation/editing works in any language
- Auto-generated prompts include language instruction

---

## Estimated Complexity

- **Development Time**: 8-10 hours
- **Testing Time**: 4-6 hours
- **Total**: 12-16 hours

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI ignores language prefix | High | Test with all 13 languages, refine prefix format |
| Breaking existing experts | Medium | Keep YAML configs as source, no changes needed |
| Locale file cleanup errors | Low | Automated script + manual verification |
| Translation quality issues | Medium | Users can create experts in any language |

---

## Conclusion

This refactoring is **HIGHLY FEASIBLE** and actually **ENHANCED** by the language persistence feature we just implemented. The persistent language preference provides a reliable source for runtime language injection, making the architecture cleaner and more maintainable.

**Key Insight:**
- Language persistence = "What language does the user want?"
- Language prefix = "How do we tell the AI to use that language?"
- Separation of concerns = "Where do we store expert content?"

All three pieces work together harmoniously.
