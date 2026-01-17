# Template System Guide

This guide explains ExpertGPTs' template-based architecture for generating expert pages.

## Overview

ExpertGPTs uses a **master template** (`templates/template.py`) to generate all expert pages. This ensures consistent UI/UX across all experts while maintaining the DRY principle.

## How It Works

### Template-Based Generation Process

```
┌─────────────────────────────────────────────────────────────┐
│  1. User creates expert via UI (Home page)                  │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PageGenerator generates unique expert ID                │
│     Example: "1005_sql_expert"                              │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Expert config created (configs/1005_sql_expert.yaml)    │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Template read (templates/template.py)                   │
│     Contains placeholders: {{EXPERT_ID}}, {{EXPERT_NAME}}   │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Placeholders replaced with expert-specific values       │
│     {{EXPERT_ID}} → 1005_sql_expert                         │
│     {{EXPERT_NAME}} → SQL Expert                            │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Expert page generated (pages/1005_sql_expert.py)        │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  7. Navigation to new expert page                           │
└─────────────────────────────────────────────────────────────┘
```

## Template Structure

### Template File

**Location**: `templates/template.py`

**Purpose**: Master template for all expert pages

**Placeholders**:
- `{{EXPERT_ID}}` - Unique expert identifier
- `{{EXPERT_NAME}}` - Display name of the expert

### Example Template Structure

```python
# templates/template.py

import streamlit as st
from utils.config_manager import ConfigManager
from utils.llm_client import LLMClient
from utils.chat_history_manager import ChatHistoryManager
from utils.i18n import i18n

# Expert configuration
EXPERT_ID = "{{EXPERT_ID}}"
EXPERT_NAME = "{{EXPERT_NAME}}"

# Page config
st.set_page_config(
    page_title=f"{EXPERT_NAME}",
    page_icon=":material/psychology:",
    layout="wide"
)

# Load expert configuration
config_manager = ConfigManager()
config = config_manager.load_config(EXPERT_ID)

# Initialize session state for this expert
if f"messages_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"messages_{EXPERT_ID}"] = []

# ... rest of the page logic
```

### Generated Expert Page

**Location**: `pages/{expert_id}.py`

**Example**: `pages/1005_sql_expert.py`

After placeholder replacement:
```python
# pages/1005_sql_expert.py

import streamlit as st
from utils.config_manager import ConfigManager
from utils.llm_client import LLMClient
from utils.chat_history_manager import ChatHistoryManager
from utils.i18n import i18n

# Expert configuration
EXPERT_ID = "1005_sql_expert"
EXPERT_NAME = "SQL Expert"

# Page config
st.set_page_config(
    page_title=f"SQL Expert",
    page_icon=":material/psychology:",
    layout="wide"
)

# Load expert configuration
config_manager = ConfigManager()
config = config_manager.load_config("1005_sql_expert")

# Initialize session state for this expert
if f"messages_1005_sql_expert" not in st.session_state:
    st.session_state[f"messages_1005_sql_expert"] = []

# ... rest of the page logic
```

## Page Numbering Scheme

### Reserved Numbers

| Number | Page | Type | Description |
|--------|------|------|-------------|
| **1000** | Home | Permanent | Expert list and management |
| **1001-9998** | Experts | Generated | Individual expert pages |
| **9999** | Settings | Permanent | App settings and configuration |

### Expert ID Generation

**Format**: `{number}_{sanitized_name}`

**Examples**:
- `1001_python_expert`
- `1002_data_scientist`
- `1005_sql_expert`
- `1010_career_coach`

**Sanitization Rules**:
- Convert to lowercase
- Replace spaces/hyphens with underscores
- Remove special characters
- Limit to alphanumeric and underscores

**Implementation**: `utils/helpers.py` - `sanitize_name()` function

## Regenerating Expert Pages

### When to Regenerate

**Regenerate all expert pages when**:
- You modify `templates/template.py`
- You add new features to expert pages
- You fix bugs in expert page logic
- You update UI/UX patterns

**Do NOT regenerate when**:
- You only edit Home or Settings pages (they're permanent)
- You only modify expert YAML configs
- You only change utility functions

### Regeneration Process

**Via Script**:
```bash
echo "yes" | python3 scripts/reset_application.py
```

**What Happens**:
1. Deletes all expert pages (`pages/1001_*.py` to `pages/9998_*.py`)
2. Runs `setup.py` to recreate from template
3. All expert pages regenerated with latest template

**Warning**: This deletes all expert pages and recreates them. Custom edits to individual expert pages will be lost.

**Best Practice**: Keep all expert-specific logic in the template or in YAML configs. Never edit generated expert pages directly.

## Permanent vs. Generated Pages

### Permanent Pages

**Home Page** (`pages/1000_Home.py`):
- Not generated from template
- Manually maintained
- Contains expert management UI
- "Add Chat" functionality

**Settings Page** (`pages/9998_Settings.py`):
- Not generated from template
- Manually maintained
- Settings for API keys, theme, language, defaults

**Help Page** (`pages/9999_Help.py`):
- Not generated from template
- Manually maintained
- Displays documentation from `docs/` directory

**Characteristics**:
- Committed to git
- Edited directly
- Not affected by `reset_application.py`

### Generated Expert Pages

**Expert Pages** (`pages/1001_*.py` to `pages/9998_*.py`):
- Generated from template
- Auto-generated, not manually edited
- Regenerated via `reset_application.py`

**Characteristics**:
- Can be gitignored or committed
- Should NOT be manually edited
- Always regenerate from template

## Modifying the Template

### Adding New Features to All Experts

**Workflow**:
1. Edit `templates/template.py`
2. Test with one expert first
3. Run `reset_application.py` to regenerate all
4. Test multiple experts to verify
5. Commit changes

**Example**: Add "Export Chat" button to all expert pages

```python
# In templates/template.py

# Add export button
if st.button("Export Chat"):
    chat_history = st.session_state[f"messages_{EXPERT_ID}"]
    # Export logic here
```

Then regenerate:
```bash
echo "yes" | python3 scripts/reset_application.py
```

All expert pages now have the export button.

### Template Modification Best Practices

**DO ✅**:
- Test changes with one expert before regenerating all
- Keep template modular and readable
- Add comments for complex logic
- Follow DRY principle within template
- Use utility functions for common operations

**DON'T ❌**:
- Edit generated expert pages directly
- Skip testing before regenerating
- Make breaking changes without considering existing experts
- Hardcode values that should be in YAML configs

## Template Components

### Page Configuration

```python
st.set_page_config(
    page_title=f"{EXPERT_NAME}",
    page_icon=":material/psychology:",
    layout="wide"
)
```

### Expert Config Loading

```python
config_manager = ConfigManager()
config = config_manager.load_config(EXPERT_ID)
```

### Session State Initialization

```python
# Messages history
if f"messages_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"messages_{EXPERT_ID}"] = []

# Provider selection
if f"provider_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"provider_{EXPERT_ID}"] = "deepseek"

# Model selection
if f"model_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"model_{EXPERT_ID}"] = config.get("metadata", {}).get("model", "deepseek-chat")

# Temperature
if f"temperature_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"temperature_{EXPERT_ID}"] = config.get("temperature", 0.7)

# Thinking level
if f"thinking_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"thinking_{EXPERT_ID}"] = "none"
```

### Chat Interface

```python
# Display chat history
for message in st.session_state[f"messages_{EXPERT_ID}"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(f"Chat with {EXPERT_NAME}"):
    # Add user message to history
    st.session_state[f"messages_{EXPERT_ID}"].append({
        "role": "user",
        "content": prompt
    })

    # Generate response
    # ... LLM API call ...

    # Add assistant response to history
    st.session_state[f"messages_{EXPERT_ID}"].append({
        "role": "assistant",
        "content": response
    })

    # Save chat history
    chat_history_manager.save_chat_history(EXPERT_ID, st.session_state[f"messages_{EXPERT_ID}"])
```

### Sidebar Controls

```python
with st.sidebar:
    st.title(f"{EXPERT_NAME}")

    # Provider selection
    provider = st.selectbox(
        "Provider",
        ["deepseek", "openai", "zai"],
        index=["deepseek", "openai", "zai"].index(st.session_state[f"provider_{EXPERT_ID}"])
    )
    st.session_state[f"provider_{EXPERT_ID}"] = provider

    # Model selection
    # ... similar for model, temperature, thinking level ...
```

## Advantages of Template System

### 1. DRY Principle

**Before Template**: Each expert page coded separately
```python
# pages/1001_python_expert.py
# 300+ lines of expert-specific code

# pages/1002_data_scientist.py
# 300+ lines of nearly identical code
# ❌ Violates DRY principle
```

**After Template**: Single template for all experts
```python
# templates/template.py
# 300 lines of template code
# Generated to 1001_python_expert.py, 1002_data_scientist.py, etc.
# ✅ Follows DRY principle
```

### 2. Consistent UI/UX

All experts have:
- Same layout
- Same controls
- Same behavior
- Same user experience

### 3. Easy Maintenance

**Adding a feature**: Update template once, regenerate all

**Example**: Add "Clear Chat" button
```bash
# 1. Add button to template (1 file)
vim templates/template.py

# 2. Regenerate all expert pages
echo "yes" | python3 scripts/reset_application.py

# 3. Done! All experts now have "Clear Chat" button
```

### 4. Scalability

**Adding 100 experts**:
- Without template: Write 100 × 300 lines = 30,000 lines
- With template: Write 1 × 300 lines = 300 lines (template) + 100 configs

**Efficiency gain**: 99% reduction in code

## Limitations and Considerations

### 1. All Experts Share Same UI

**Limitation**: Cannot have expert-specific UI without template logic

**Workaround**: Use conditional logic in template based on config values

**Example**:
```python
# In template
if config.get("custom_ui"):
    # Render custom UI
else:
    # Render standard UI
```

### 2. Regeneration Overwrites Custom Edits

**Limitation**: Manual edits to generated pages are lost on regeneration

**Solution**: Never edit generated pages. Always update template instead.

### 3. Regeneration Affects All Experts

**Limitation**: Cannot regenerate individual experts

**Solution**: Test thoroughly before regenerating all

## Best Practices

### 1. Keep Expert Logic in Configs

**Good**:
```yaml
# configs/1001_python_expert.yaml
system_prompt: |
  Custom Python-specific instructions...
```

**Bad**:
```python
# In template
if EXPERT_ID == "1001_python_expert":
    # Python-specific logic
```

### 2. Use Utility Functions

**Good**:
```python
# In template
from utils.helpers import get_expert_welcome_message

st.markdown(get_expert_welcome_message(config))
```

**Bad**:
```python
# In template - duplicate logic
if EXPERT_ID == "1001_python_expert":
    st.markdown("Welcome to Python Expert...")
elif EXPERT_ID == "1002_data_scientist":
    st.markdown("Welcome to Data Scientist...")
```

### 3. Test Before Regenerating

**Workflow**:
1. Edit template
2. Create test expert
3. Verify feature works
4. Delete test expert
5. Regenerate all experts
6. Test multiple experts

## Troubleshooting

### Template Changes Not Appearing

**Problem**: Modified template but expert pages unchanged

**Solution**:
```bash
# Regenerate expert pages
echo "yes" | python3 scripts/reset_application.py
```

### Regeneration Failed

**Problem**: Error during regeneration

**Common Causes**:
1. Syntax error in template
2. Missing utility functions
3. Invalid placeholder names

**Solution**:
1. Check template for syntax errors
2. Verify all imports exist
3. Check placeholder names: `{{EXPERT_ID}}`, `{{EXPERT_NAME}}`

### Expert Page Not Loading

**Problem**: Navigation to expert page shows error

**Possible Cause**: Expert page out of sync with template

**Solution**:
```bash
# Regenerate all pages
echo "yes" | python3 scripts/reset_application.py
```

## Related Documentation

- **[Architecture Overview](overview.md)** - System architecture
- **[Development - Adding Features](../development/adding-features.md)** - Feature development
- **[Configuration - Expert Configs](../configuration/expert-configs.md)** - Expert YAML configs

---

**Back to**: [Documentation Home](../README.md) | [Architecture Overview](overview.md)
