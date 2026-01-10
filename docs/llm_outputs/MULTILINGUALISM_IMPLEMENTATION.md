# Multilingualism Implementation for ExpertGPTs

## User Request

> The application should support multilingualism; what suggestions do you have on how this can be implemented?

## Context

ExpertGPTs is a Streamlit-based multi-expert AI chat application with:
- Dynamic page generation
- Template-based expert creation
- Settings/Configuration management
- Multiple LLM providers

## Analysis: Translation Scope

### What Needs Translation

1. **UI Elements** (Primary concern)
   - Button labels ("Add Chat", "Create Expert", "Cancel")
   - Status messages ("API key configured", "No expert agents found")
   - Form labels ("Expert Name", "Temperature", "LLM Provider")
   - Help text and captions
   - Navigation items

2. **Dynamic Content** (Secondary)
   - Expert names (user-generated, but could have translated display names)
   - System prompts (expert behavior)
   - Error messages

3. **Configuration** (Metadata)
   - App title, descriptions
   - Theme settings labels

## Implementation Options

### Option 1: Simple Dictionary-Based i18n (Quick Start)

**Best for:** Small-scale, few languages, rapid implementation

#### Architecture

```python
# utils/i18n.py
TRANSLATIONS = {
    "en": {
        "home.title": "Welcome to ExpertGPTs",
        "home.no_experts": "No expert agents found. Create your first expert from Settings!",
        "buttons.add_chat": "Add Chat",
        "buttons.create_expert": "Create Expert",
        # ... more keys
    },
    "de": {
        "home.title": "Willkommen bei ExpertGPTs",
        "home.no_experts": "Keine Experten gefunden. Erstellen Sie Ihren ersten Experten in den Einstellungen!",
        "buttons.add_chat": "Chat hinzufügen",
        "buttons.create_expert": "Experten erstellen",
    },
    "es": { ... },
    "fr": { ... }
}

def t(key: str, lang: str = None) -> str:
    """Get translation for a key."""
    if lang is None:
        lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, {}).get(key, key)
```

#### Usage

```python
# In pages
from utils.i18n import t

st.title(t("home.title"))
st.button(t("buttons.add_chat"))
```

#### Pros & Cons

**Pros:**
- ✅ Fast to implement
- ✅ No external dependencies
- ✅ Simple to understand
- ✅ Works well for small projects

**Cons:**
- ❌ Hard to maintain as translations grow
- ❌ No pluralization support
- ❌ No interpolation support
- ❌ Missing keys fall back silently

---

### Option 2: Streamlit-i18n Integration (Balanced) ⭐ RECOMMENDED

**Best for:** Production apps, maintainability, community standards

#### Architecture

```python
# pip install streamlit-i18n

# utils/i18n.py
import streamlit as st
from streamlit_javascript import st_javascript
import json
from pathlib import Path

class I18nManager:
    def __init__(self):
        self.translations = {}
        self.current_lang = "en"
        self.load_translations()

    def load_translations(self):
        """Load translation files from locales/ directory."""
        locales_dir = Path(__file__).parent.parent / "locales"
        for lang_file in locales_dir.glob("*.json"):
            lang = lang_file.stem
            with open(lang_file, "r", encoding="utf-8") as f:
                self.translations[lang] = json.load(f)

    def t(self, key: str, **kwargs) -> str:
        """Get translated string with interpolation."""
        lang = st.session_state.get("language", "en")
        template = self.translations.get(lang, {}).get(key, key)
        return template.format(**kwargs)

    def get_available_languages(self):
        """Get list of available languages."""
        return list(self.translations.keys())

    def set_language(self, lang: str):
        """Set current language."""
        if lang in self.translations:
            st.session_state.language = lang
            st.rerun()

i18n = I18nManager()
```

#### File Structure

```
locales/
├── en.json
├── de.json
├── es.json
└── fr.json
```

#### locales/en.json

```json
{
  "home": {
    "title": "Welcome to ExpertGPTs",
    "subtitle": "Your Multi-Expert AI Assistant Platform",
    "no_experts": "No expert agents found. Create your first expert from Settings!"
  },
  "buttons": {
    "add_chat": "Add Chat",
    "create_expert": "Create Expert",
    "cancel": "Cancel",
    "delete": "Delete",
    "save": "Save"
  },
  "status": {
    "api_key_configured": "API key configured",
    "api_key_not_set": "API key not set"
  },
  "forms": {
    "expert_name": "Expert Name",
    "description": "Agent Description",
    "temperature": "Temperature"
  }
}
```

#### Usage

```python
# In pages
from utils.i18n import i18n

st.title(i18n.t("home.title"))
st.button(i18n.t("buttons.add_chat"))
st.info(i18n.t("home.no_experts"))
```

#### Add Language Selector to Settings

```python
# In pages/9999_Settings.py

st.subheader("🌐 Language / Sprache / Langue")

available_langs = i18n.get_available_languages()
lang_names = {
    "en": "🇺🇸 English",
    "de": "🇩🇪 Deutsch",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français"
}

current_lang = st.session_state.get("language", "en")
lang_index = available_langs.index(current_lang) if current_lang in available_langs else 0

selected_lang = st.selectbox(
    "Select Language / Sprache wählen / Sélectionner la langue",
    options=available_langs,
    format_func=lambda x: lang_names.get(x, x),
    index=lang_index,
    key="language_selector"
)

if selected_lang != current_lang:
    i18n.set_language(selected_lang)
```

#### Pros & Cons

**Pros:**
- ✅ JSON files are easy to edit
- ✅ Separation of concerns
- ✅ Easy to add new languages
- ✅ Can use translation tools (POEditor, Lokalise)
- ✅ Nested structure for organization
- ✅ String interpolation support

**Cons:**
- ❌ Requires managing JSON files
- ❌ Still no pluralization
- ❌ Need to reload app to change language

---

### Option 3: Professional i18n with GNU gettext (Enterprise)

**Best for:** Large-scale, professional, production apps

#### Architecture

```python
# pip install gettext

# utils/i18n.py
import gettext
import streamlit as st
from pathlib import Path

class I18nManager:
    def __init__(self):
        self.current_lang = "en"
        self.translations = {}
        self.setup_translations()

    def setup_translations(self):
        """Setup gettext translations."""
        locales_dir = Path(__file__).parent.parent / "locales"

        # Load all available languages
        for lang_dir in locales_dir.iterdir():
            if lang_dir.is_dir() and not lang_dir.name.startswith("_"):
                lang = lang_dir.name
                try:
                    translator = gettext.translation(
                        "expertgpts",
                        localedir=locales_dir,
                        languages=[lang],
                        fallback=True
                    )
                    self.translations[lang] = translator
                except Exception as e:
                    print(f"Failed to load {lang}: {e}")

    def t(self, key: str, **kwargs) -> str:
        """Get translated string."""
        lang = st.session_state.get("language", "en")

        if lang in self.translations:
            self.translations[lang].install()
            return _(key).format(**kwargs)
        return key

    def set_language(self, lang: str):
        """Set current language."""
        st.session_state.language = lang
        st.rerun()

i18n = I18nManager()
```

#### File Structure

```
locales/
├── en/
│   └── LC_MESSAGES/
│       ├── expertgpts.po
│       └── expertgpts.mo
├── de/
│   └── LC_MESSAGES/
│       ├── expertgpts.po
│       └── expertgpts.mo
└── es/
    └── LC_MESSAGES/
        ├── expertgpts.po
        └── expertgpts.mo
```

#### Template (pot file)

```pot
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"

#: pages/1000_Home.py:17
msgid "No expert agents found. Create your first expert from Settings!"
msgstr ""

#: utils/dialogs.py:468
msgid "Create Expert"
msgstr ""
```

#### German translation (de/LC_MESSAGES/expertgpts.po)

```po
msgid "No expert agents found. Create your first expert from Settings!"
msgstr "Keine Experten gefunden. Erstellen Sie Ihren ersten Experten in den Einstellungen!"

msgid "Create Expert"
msgstr "Experten erstellen"
```

#### Usage

```python
# In pages (no import needed if using gettext.install())
from utils.i18n import i18n

st.title(_("Welcome to ExpertGPTs"))
st.button(_("Add Chat"))
```

#### Pros & Cons

**Pros:**
- ✅ Industry standard for professional apps
- ✅ Pluralization support
- ✅ Context support
- ✅ Professional translation tools support
- ✅ Works with translation services
- ✅ Handles complex grammar rules

**Cons:**
- ❌ Steep learning curve
- ❌ More complex setup
- ❌ Requires .po/.mo file compilation
- ❌ Overkill for small projects

---

### Option 4: Hybrid Approach (Recommended for ExpertGPTs)

**Best for:** Your specific use case - flexibility with professional structure

Combine JSON for simple UI + specialized handling for expert prompts:

#### Architecture

```python
# utils/i18n.py

class I18nManager:
    def __init__(self):
        self.ui_translations = {}  # JSON for UI
        self.prompt_translations = {}  # JSON for system prompts
        self.current_lang = "en"
        self.load_all_translations()

    def load_all_translations(self):
        """Load both UI and prompt translations."""
        locales_dir = Path(__file__).parent.parent / "locales"

        # Load UI translations
        for lang_file in (locales_dir / "ui").glob("*.json"):
            lang = lang_file.stem
            with open(lang_file, "r", encoding="utf-8") as f:
                self.ui_translations[lang] = json.load(f)

        # Load prompt translations
        for lang_file in (locales_dir / "prompts").glob("*.json"):
            lang = lang_file.stem
            with open(lang_file, "r", encoding="utf-8") as f:
                self.prompt_translations[lang] = json.load(f)

    def t(self, key: str, **kwargs) -> str:
        """Translate UI element."""
        lang = st.session_state.get("language", "en")
        template = self._get_nested(self.ui_translations, lang, key)
        return template.format(**kwargs) if template else key

    def translate_prompt(self, expert_id: str, lang: str = None) -> str:
        """Get translated system prompt for an expert."""
        if lang is None:
            lang = st.session_state.get("language", "en")

        prompts = self.prompt_translations.get(lang, {})
        return prompts.get(expert_id, prompts.get("default", ""))

    def _get_nested(self, data, lang, key):
        """Get nested value from dict using dot notation."""
        keys = key.split(".")
        value = data.get(lang, {})
        for k in keys:
            value = value.get(k, {})
        return value if isinstance(value, str) else None

i18n = I18nManager()
```

#### File Structure

```
locales/
├── ui/
│   ├── en.json
│   ├── de.json
│   └── es.json
└── prompts/
    ├── en.json
    ├── de.json
    └── es.json
```

#### locales/ui/en.json

```json
{
  "nav": {
    "home": "Home",
    "settings": "Settings"
  },
  "home": {
    "title": "Welcome to ExpertGPTs",
    "no_experts": "No expert agents found. Create your first expert from Settings!"
  }
}
```

#### locales/prompts/de.json

```json
{
  "default": "Sie sind ein hilfreicher Assistent.",
  "1001_python_expert": "Sie sind ein Experte für Python-Programmierung...",
  "1006_translation_expert": "Sie sind ein Übersetzungsexperte für Deutsch und Englisch..."
}
```

#### Pros & Cons

**Pros:**
- ✅ Separates UI from expert behavior
- ✅ Flexible for different use cases
- ✅ JSON-based (easy to edit)
- ✅ Can translate prompts independently
- ✅ Supports per-expert language settings

**Cons:**
- ❌ More complex structure
- ❌ Need to maintain two sets of translations
- ❌ Expert prompts require more thought

---

## Special Considerations for ExpertGPTs

### 1. Expert Names & Descriptions

**Challenge:** User creates experts in one language, another user wants different language

#### Solution A: Single-language experts

```python
# Expert config has language field
{
  "expert_id": "1001_python_expert",
  "expert_name": "Python Expert",  # Always in English
  "language": "en",  # Prompt language
  "description": "Expert in Python programming..."
}
```

#### Solution B: Multi-language display

```python
# Expert config with translations
{
  "expert_id": "1001_python_expert",
  "names": {
    "en": "Python Expert",
    "de": "Python-Experte",
    "es": "Experto en Python"
  },
  "descriptions": {
    "en": "Expert in Python programming...",
    "de": "Experte für Python-Programmierung...",
  }
}
```

### 2. System Prompts in Different Languages

**Current:** Experts have system prompts in their creation language

**Solution:** Store language in config, translate on load

```python
# In template.py
system_prompt = expert_config["system_prompt"]
expert_lang = expert_config.get("language", "en")

# If UI language differs from expert language, show warning
if st.session_state.language != expert_lang:
    st.warning(f"⚠️ This expert operates in {get_language_name(expert_lang)}")
```

### 3. Settings Page Language Selector

```python
# Add to Settings → General tab
st.subheader("🌐 Language")

languages = {
    "en": {"name": "English", "flag": "🇺🇸"},
    "de": {"name": "Deutsch", "flag": "🇩🇪"},
    "es": {"name": "Español", "flag": "🇪🇸"},
    "fr": {"name": "Français", "flag": "🇫🇷"}
}

current = st.session_state.get("language", "en")
cols = st.columns(len(languages))

for idx, (code, info) in enumerate(languages.items()):
    with cols[idx]:
        if st.button(f"{info['flag']} {info['name']}", use_container_width=True):
            st.session_state.language = code
            st.rerun()
```

---

## Recommended Implementation Plan

### Phase 1: Foundation (1-2 days)

**Choose Option 2 (JSON-based)** - Best balance of simplicity and power

**Tasks:**
1. Create i18n infrastructure:
   ```bash
   mkdir -p locales/ui
   touch utils/i18n.py
   ```
2. Extract existing strings to `en.json`
3. Add language selector to Settings page
4. Update Home page as proof of concept
5. Initialize default language in session state

### Phase 2: Core Pages (2-3 days)

**Tasks:**
1. Translate Home page (`pages/1000_Home.py`)
2. Translate Settings page (`pages/9999_Settings.py`)
3. Translate dialogs (`utils/dialogs.py`)
4. Translate app.py (navigation)
5. Update all status messages and error messages

### Phase 3: Expert Templates (1-2 days)

**Tasks:**

**Option A: Translate UI only**
- Keep expert prompts in user's language
- Add language metadata to expert configs
- Show language indicator in UI

**Option B: Translate expert prompts too**
- Store translations for each expert's system prompt
- Load appropriate prompt based on UI language
- Allow per-expert language override

### Phase 4: Additional Languages (Ongoing)

**Tasks:**
1. Add German (you already have Translation Expert)
2. Add other priority languages
3. Set up translation workflow
4. Consider professional translation services
5. Add pluralization support if needed

---

## Quick Start Implementation (Option 2)

### Step 1: Create i18n Manager

```python
# utils/i18n.py
import json
import streamlit as st
from pathlib import Path
from typing import Dict, Any

class I18nManager:
    """Internationalization manager for ExpertGPTs."""

    def __init__(self):
        self.translations: Dict[str, Dict] = {}
        self.current_lang: str = "en"
        self.load_translations()

    def load_translations(self):
        """Load translation files from locales/ directory."""
        locales_dir = Path(__file__).parent.parent / "locales" / "ui"

        if not locales_dir.exists():
            print(f"Warning: Locales directory not found: {locales_dir}")
            return

        for lang_file in locales_dir.glob("*.json"):
            lang = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
            except Exception as e:
                print(f"Error loading {lang}: {e}")

    def t(self, key: str, **kwargs) -> str:
        """Get translated string with interpolation.

        Args:
            key: Translation key using dot notation (e.g., "home.title")
            **kwargs: Variables for string interpolation

        Returns:
            Translated string, or key if not found
        """
        lang = st.session_state.get("language", "en")
        template = self._get_nested(self.translations, lang, key)

        if template is None:
            return key  # Fallback to key if translation not found

        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template  # Return template if formatting fails

    def get_available_languages(self) -> list:
        """Get list of available language codes."""
        return list(self.translations.keys())

    def get_language_name(self, code: str) -> str:
        """Get human-readable language name."""
        names = {
            "en": "English",
            "de": "Deutsch",
            "es": "Español",
            "fr": "Français",
        }
        return names.get(code, code.upper())

    def set_language(self, lang: str):
        """Set current language and rerun app."""
        if lang in self.translations:
            st.session_state.language = lang
            st.rerun()
        else:
            print(f"Warning: Language '{lang}' not available")

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
```

### Step 2: Create Locales Structure

```bash
mkdir -p locales/ui
```

### Step 3: Create English Translation File

```json
// locales/ui/en.json
{
  "nav": {
    "home": "Home",
    "settings": "Settings"
  },
  "home": {
    "title": "Welcome to ExpertGPTs",
    "subtitle": "Your Multi-Expert AI Assistant Platform",
    "no_experts": "No expert agents found. Create your first expert from Settings!",
    "available_experts": "Available Expert Agents"
  },
  "buttons": {
    "add_chat": "Add Chat",
    "create_expert": "Create Expert",
    "cancel": "Cancel",
    "delete": "Delete",
    "save": "Save",
    "go_to_settings": "Go to Settings"
  },
  "status": {
    "api_key_configured": "API key configured",
    "api_key_not_set": "API key not set"
  },
  "forms": {
    "expert_name": "Expert Name",
    "description": "Agent Description",
    "temperature": "Temperature",
    "llm_provider": "LLM Provider",
    "model": "Model"
  },
  "language": {
    "title": "Language",
    "select": "Select Language"
  }
}
```

### Step 4: Create German Translation File

```json
// locales/ui/de.json
{
  "nav": {
    "home": "Startseite",
    "settings": "Einstellungen"
  },
  "home": {
    "title": "Willkommen bei ExpertGPTs",
    "subtitle": "Ihre Multi-Expert-KI-Assistenten-Plattform",
    "no_experts": "Keine Experten gefunden. Erstellen Sie Ihren ersten Experten in den Einstellungen!",
    "available_experts": "Verfügbare Experten"
  },
  "buttons": {
    "add_chat": "Chat hinzufügen",
    "create_expert": "Experten erstellen",
    "cancel": "Abbrechen",
    "delete": "Löschen",
    "save": "Speichern",
    "go_to_settings": "Zu den Einstellungen"
  },
  "status": {
    "api_key_configured": "API-Schlüssel konfiguriert",
    "api_key_not_set": "API-Schlüssel nicht festgelegt"
  },
  "forms": {
    "expert_name": "Expertenname",
    "description": "Agentenbeschreibung",
    "temperature": "Temperatur",
    "llm_provider": "LLM-Anbieter",
    "model": "Modell"
  },
  "language": {
    "title": "Sprache",
    "select": "Sprache wählen"
  }
}
```

### Step 5: Initialize Language in Session State

```python
# utils/session_state.py

def initialize_shared_session_state():
    """Initialize shared session state variables across all pages."""
    # ... existing code ...

    # Initialize default language
    if "language" not in st.session_state:
        st.session_state.language = "en"  # Default to English
```

### Step 6: Update Home Page

```python
# pages/1000_Home.py
from utils.i18n import i18n

def render_expert_list():
    """Render a list of available expert agents."""
    config_manager = ConfigManager()
    experts = config_manager.list_experts()

    if not experts:
        st.info(f"🔍 {i18n.t('home.no_experts')}")
        return

    st.subheader(f"📚 {i18n.t('home.available_experts')}")

    # ... rest of the code ...

def main():
    """Render the home page content."""
    # Render sidebar
    with st.sidebar:
        # Toolbox
        st.caption("**Toolbox**")
        if st.button(f"➕ {i18n.t('buttons.add_chat')}", width="stretch"):
            st.session_state.show_add_chat_dialog = True
            st.rerun()

        # ... rest of the code ...

    st.title(f"🤖 {i18n.t('home.title')}")

    st.markdown(f"""
    ## {i18n.t('home.subtitle')}

    ### Getting Started

    1. **Set your API Key**: Enter your DeepSeek API key in Settings
    2. **Choose an Expert**: Select an expert agent from the navigation menu
    3. **Start Chatting**: Ask questions and get expert-level responses
    """)
```

### Step 7: Add Language Selector to Settings

```python
# pages/9999_Settings.py
from utils.i18n import i18n

# In the General tab
st.subheader(f"🌐 {i18n.t('language.title')}")

available_langs = i18n.get_available_languages()
lang_names = {
    "en": "🇺🇸 English",
    "de": "🇩🇪 Deutsch",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français"
}

current_lang = st.session_state.get("language", "en")
lang_index = available_langs.index(current_lang) if current_lang in available_langs else 0

selected_lang = st.selectbox(
    i18n.t("language.select"),
    options=available_langs,
    format_func=lambda x: lang_names.get(x, x),
    index=lang_index,
    key="language_selector"
)

if selected_lang != current_lang:
    i18n.set_language(selected_lang)
```

---

## Estimated Effort

- **Phase 1 (Foundation):** 2-3 hours
  - Create i18n manager
  - Set up file structure
  - Extract English strings
  - Add language selector

- **Phase 2 (Core pages):** 4-6 hours
  - Home page
  - Settings page
  - Dialogs
  - Navigation

- **Phase 3 (Templates):** 2-3 hours
  - Template.py
  - Per-expert language handling

- **Total:** ~1-2 days for basic multilingual support

---

## Translation Workflow Recommendations

### For Development

1. **Extract strings** to `en.json` as you code
2. **Keep English as source of truth** - always update en.json first
3. **Mark missing translations** with placeholders like `"TODO: Translate this"`

### For Production

1. **Use translation tools:**
   - POEditor (supports JSON)
   - Lokalise (supports JSON)
   - Crowdin (supports JSON)

2. **Professional translation:**
   - Hire translators for target languages
   - Provide context for each string
   - Review translations in context

3. **Community translation:**
   - Allow users to contribute translations
   - Set up GitHub workflow for PRs
   - Credit contributors

---

## Testing Checklist

- [ ] All UI strings are translatable
- [ ] Language switching works without page reload
- [ ] Missing translations fall back gracefully
- [ ] Expert names/descriptions display correctly
- [ ] System prompts use correct language
- [ ] Error messages are translated
- [ ] Date/number formats respect locale
- [ ] Right-to-left languages work (if applicable)

---

## Next Steps

1. **Choose implementation option** (recommend Option 2)
2. **Create infrastructure** (i18n manager, locales directory)
3. **Start with proof of concept** (Home page + language selector)
4. **Expand to core pages** (Settings, dialogs)
5. **Handle expert-specific translations** (prompts, descriptions)
6. **Add more languages** as needed
7. **Set up translation workflow** for ongoing maintenance

---

## Conclusion

Multilingual support is achievable with the right architecture. The JSON-based approach (Option 2) provides the best balance of:

- **Simplicity** - Easy to understand and maintain
- **Flexibility** - Easy to add new languages
- **Performance** - Minimal overhead
- **Scalability** - Can grow with the application

Start small, iterate, and expand based on user needs!
