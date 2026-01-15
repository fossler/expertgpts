# I18N Refactoring - Visual Demonstration

## What Happens When User Interacts with an Expert

### Scenario: German User Chats with Python Expert

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USER OPENS APP                                              │
│                                                                 │
│  App reads .streamlit/config.toml:                              │
│  [language]                                                     │
│  code = "de"                                                    │
│                                                                 │
│  Result: st.session_state.language = "de"                      │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. USER NAVIGATES TO PYTHON EXPERT                             │
│                                                                 │
│  App loads: configs/1001_python_expert.yaml                     │
│                                                                 │
│  expert_id: 1001_python_expert                                  │
│  expert_name: Python Expert                                     │
│  description: Expert in Python programming...                   │
│  system_prompt: You are Python Expert...                        │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. USER SENDS MESSAGE: "How do I read a file in Python?"      │
│                                                                 │
│  In templates/template.py:                                      │
│                                                                 │
│  # Get language prefix for German                               │
│  language_prefix = i18n.get_language_prefix()                   │
│  # Returns: "You must respond in German (Deutsch)."            │
│                                                                 │
│  # Get raw system prompt from YAML                              │
│  raw_system_prompt = config.get('system_prompt')               │
│  # Returns: "You are Python Expert..."                         │
│                                                                 │
│  # Combine them                                                 │
│  system_prompt_with_lang = f"{language_prefix}\n\n{raw_prompt}" │
│                                                                 │
│  Result sent to API:                                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ You must respond in German (Deutsch).                  │    │
│  │                                                         │    │
│  │ You are Python Expert, a domain-specific expert...     │    │
│  │ Expert in Python programming, software development...  │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. API RECEIVES PROMPT AND RESPONDS                            │
│                                                                 │
│  DeepSeek API receives:                                         │
│  - Clear instruction: "Respond in German (Deutsch)"            │
│  - Expert context: Python Expert                                │
│  - User question: "How do I read a file in Python?"            │
│                                                                 │
│  AI understands it should:                                      │
│  1. Respond in German                                           │
│  2. Act as Python Expert                                        │
│  3. Answer the question about file reading                     │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. AI RESPONDS IN GERMAN                                       │
│                                                                 │
│  Expected response:                                             │
│  "Um eine Datei in Python zu lesen, können Sie die              │
│   built-in open() Funktion verwenden..."                        │
│   (Translation: "To read a file in Python, you can use...")     │
│                                                                 │
│  ✅ AI responds in German as instructed                         │
│  ✅ Content is Python-expert level                              │
│  ✅ Answer addresses the user's question                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Before vs After Refactoring

### BEFORE (Data Duplication)

**Expert content existed in 14 places:**

```
configs/1001_python_expert.yaml:
  expert_name: Python Expert
  system_prompt: You are Python Expert...

locales/ui/en.json:
  experts:
    python_expert:
      name: Python Expert
      system_prompt: You are Python Expert...

locales/ui/de.json:
  experts:
    python_expert:
      name: Python Experte
      system_prompt: Sie sind Python-Experte...

locales/ui/es.json:
  experts:
    python_expert:
      name: Experto en Python
      system_prompt: Usted es un experto en Python...

... and 11 more locale files
```

**Problems:**
- ❌ Same content translated 14 times
- ❌ Change description → Update 14 files
- ❌ Risk of inconsistencies
- ❌ Confusing source of truth

---

### AFTER (Clean Architecture)

**Expert content exists in 1 place:**

```
configs/1001_python_expert.yaml:
  expert_name: Python Expert
  system_prompt: You are Python Expert...

locales/ui/en.json:
  (only UI translations: buttons, labels, messages)

locales/ui/de.json:
  (only UI translations: buttons, labels, messages)

Runtime injection:
  language_prefix = "You must respond in German (Deutsch)."
  final_prompt = f"{prefix}\n\n{raw_prompt}"
```

**Benefits:**
- ✅ Expert content in 1 place (YAML)
- ✅ Change description → Update 1 file
- ✅ No inconsistencies possible
- ✅ Clear source of truth
- ✅ AI still responds in user's language

---

## Settings Page Behavior

### VIEW MODE (Read-only)

```
┌────────────────────────────────────────────────────────┐
│  Expert: Python Expert                                 │
│                                                        │
│  🧠 Expert Behavior:                                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │ You must respond in German (Deutsch).           │ │
│  │                                                  │ │
│  │ You are Python Expert, a domain-specific        │ │
│  │ expert AI assistant.                             │ │
│  │                                                  │ │
│  │ Expert in Python programming, software          │ │
│  │ development, debugging, and best practices.     │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  [disabled - cannot edit]                              │
└────────────────────────────────────────────────────────┘
```

**What the user sees:**
- Language prefix at the top (shows what language AI will use)
- Raw system prompt from YAML (in English)
- Clear understanding of what will be sent to API

---

### EDIT MODE (Can edit)

```
┌────────────────────────────────────────────────────────┐
│  Edit Expert: Python Expert                            │
│                                                        │
│  🧠 Customize Expert Behavior:                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ You are Python Expert, a domain-specific        │ │
│  │ expert AI assistant.                             │ │
│  │                                                  │ │
│  │ Expert in Python programming, software          │ │
│  │ development, debugging, and best practices.     │ │
│  │                                                  │ │
│  │ [user can edit this content]                    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  💡 The expert will automatically respond in the      │
│     user's selected language.                          │
│                                                        │
│  [💾 Save Changes]  [❌ Cancel]                        │
└────────────────────────────────────────────────────────┘
```

**What the user sees:**
- Only the raw English prompt (editable)
- Help text explains language is handled automatically
- No language prefix shown (it's added at runtime)

---

## Code Flow Visualization

### In template.py (when user sends message):

```python
# 1. Get language from config.toml
language_prefix = i18n.get_language_prefix()
# → "You must respond in German (Deutsch)."

# 2. Get raw prompt from YAML
raw_system_prompt = config.get('system_prompt')
# → "You are Python Expert..."

# 3. Combine them
system_prompt_with_lang = f"{language_prefix}\n\n{raw_system_prompt}"
# → "You must respond in German (Deutsch).\n\nYou are Python Expert..."

# 4. Send to API
client.chat_stream(
    messages=[...],
    system_prompt=system_prompt_with_lang,  # ← Includes language prefix
    ...
)
```

### In llm_client.py (when auto-generating prompt):

```python
def generate_system_prompt(expert_name, description):
    # 1. Generate prompt using LLM (result in English)
    response = self.chat(messages=[{
        "role": "user",
        "content": f"Create a system prompt for {expert_name}..."
    }])
    # → "You are Python Expert, specializing in..."

    # 2. Get language prefix
    language_prefix = i18n.get_language_prefix()
    # → "You must respond in German (Deutsch)."

    # 3. Combine them
    return f"{language_prefix}\n\n{response.strip()}"
    # → "You must respond in German (Deutsch).\n\nYou are Python Expert..."
```

---

## Real Example: German User Creates Expert

### User fills in form:

```
Name: "Datenexperte"
Description: "Experte für Datenanalyse, Visualisierung und Machine Learning"
```

### What gets saved to YAML:

```yaml
configs/1008_datenexperte.yaml:
  expert_id: 1008_datenexperte
  expert_name: Datenexperte
  description: Experte für Datenanalyse, Visualisierung und Machine Learning
  system_prompt: |
    You must respond in German (Deutsch).

    You are Datenexperte, a domain-specific expert AI assistant.

    Experte für Datenanalyse, Visualisierung und Machine Learning

    ## Guidelines
    - Provide accurate, expert-level information in your domain
    ...
```

### What user sees when chatting:

```
User: "Wie erstelle ich ein Streudiagramm mit matplotlib?"
AI: "Um ein Streudiagramm mit matplotlib zu erstellen..."
     (AI responds in German as instructed)
```

---

## Summary

The i18n refactoring successfully:

1. ✅ **Eliminated Duplication:** 14 copies → 1 copy
2. ✅ **Maintained Language Support:** AI responds in all 13 languages
3. ✅ **Improved Maintainability:** Update 1 file instead of 14
4. ✅ **Enhanced Clarity:** Clear separation of concerns
5. ✅ **Preserved Functionality:** User experience unchanged

**The app is now more maintainable while still providing full multilingual support!**
