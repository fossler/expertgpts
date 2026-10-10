# State Management Guide

This guide explains ExpertGPTs' multi-layered state management system, including session state, persistent storage, and cache invalidation.

## Overview

ExpertGPTs uses a **multi-layered state system** with different lifetimes and purposes:

```
┌─────────────────────────────────────────────────────────────┐
│  1. SHARED SESSION STATE                                    │
│  Initialized once per session                                │
│  - API keys for all providers                                │
│  - Default LLM settings                                      │
│  - Language preference                                       │
│  - Navigation state                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PER-EXPERT SESSION STATE                                │
│  Separate for each expert                                    │
│  - Messages history: messages_{expert_id}                   │
│  - Config cache version: cache_version_{expert_id}          │
│  - Attachment uploader generation: attachments_{expert_id}  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. PERSISTENT STORAGE                                      │
│  Survives app restarts                                       │
│  - Chat history: chat_history/{expert_id}.json              │
│  - Chat images: chat_attachments/{expert_id}/               │
│  - Expert configs: configs/{expert_id}.yaml                 │
│    (incl. provider, model, temperature, thinking level)     │
│  - User preferences: .streamlit/app_defaults.toml           │
│  - Theme settings: .streamlit/config.toml                   │
└─────────────────────────────────────────────────────────────┘
```

## Session State Types

### 1. Shared Session State

**Purpose**: Global settings shared across all experts

**Lifetime**: Application session (browser tab)

**Initialized By**: `lib/shared/session_state.py` - `initialize_shared_session_state()`

**State Variables**:

```python
# API Keys (loaded from secrets.toml, only providers with a key)
st.session_state.api_keys = {
    "deepseek": "sk-...",
    "openai": "sk-...",
    "zai": "...",
    "kimi": "sk-..."
}

# Default LLM Settings (loaded from app_defaults.toml via get_llm_defaults())
st.session_state.default_provider = "deepseek"
st.session_state.default_model = "deepseek-flash"
st.session_state.default_thinking_level = "none"
st.session_state.default_thinking_enabled = True  # DEFAULT_THINKING_ENABLED

# Language Preference (loaded from app_defaults.toml)
st.session_state.language = "en"  # Auto-detected on first run

# Navigation / Dialog State (set by app.py and the pages)
st.session_state.pending_expert_page = None   # handle_pending_navigation()
st.session_state.show_add_chat_dialog = False  # ensure_dialog_state("add_chat")
```

**Initialization Flow**:

```
App starts
    ↓
initialize_shared_session_state() called (every page run; each step only runs if its key is missing)
    ↓
Ensure .streamlit/config.toml exists (ensure_config_file_exists)
    ↓
Initialize language (get_language_preference, or detect_system_language + save)
    ↓
Load API keys (get_all_provider_api_keys from secrets.toml)
    ↓
Load LLM defaults (get_llm_defaults from app_defaults.toml)
```

### 2. Per-Expert Session State

**Purpose**: Expert-specific settings and conversation context

**Lifetime**: Application session (browser tab)

**Initialized By**: Individual expert pages

**State Variables Pattern**:

```python
# For each expert with ID "1001_python_expert"

# Messages History (assistant messages also carry provider/model)
st.session_state["messages_1001_python_expert"] = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "provider": "deepseek", "model": "deepseek-flash"}
]

# Cache Version (for config cache invalidation)
st.session_state["cache_version_1001_python_expert"] = 1

# Attachment uploader generation (incremented after each sent message,
# which clears the toolbox uploaders)
st.session_state["attachments_1001_python_expert"] = 3
```

The chat toolbox also keeps widget state under expert-specific keys (e.g. `{expert_id}_toolbox_model_v{version}`, `{expert_id}_model_settings_changed`, cached voice transcripts per recording).

**Provider, model, temperature and thinking level are not session state**: they are stored in the expert config (`configs/{expert_id}.yaml`) and read on every run via `get_llm_metadata(config)` and `config.get("temperature")`. The toolbox model row (`_render_model_settings()` in `lib/ui/chat_toolbox.py`) saves changes directly with `update_config()` and then calls `invalidate_expert_cache()`.

**Initialization in Expert Pages** (`templates/template.py`):

```python
EXPERT_ID = "1001_python_expert"


def initialize_session_state():
    # Initialize shared state first (API key, navigation, etc.)
    initialize_shared_session_state()

    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        # Load from file if exists, otherwise start empty
        st.session_state[messages_key] = load_chat_history(EXPERT_ID)

    return messages_key
```

`cache_version_{expert_id}` is read with a default (`st.session_state.get(f"cache_version_{EXPERT_ID}", 0)`) and only created when the cache is invalidated.

## Persistent Storage

### 1. Chat History

**Location**: `chat_history/{expert_id}.json`

**Format**: JSON

**Example**:
```json
{
  "expert_id": "1001_python_expert",
  "created_at": "2026-10-10T12:00:00.000000",
  "last_updated": "2026-10-10T12:05:00.000000",
  "messages": [
    {
      "role": "user",
      "content": "How do I read a file in Python?",
      "timestamp": "2026-10-10T12:04:50.000000"
    },
    {
      "role": "assistant",
      "content": "You can use the open() function...",
      "provider": "deepseek",
      "model": "deepseek-flash",
      "timestamp": "2026-10-10T12:05:00.000000"
    }
  ]
}
```

**Manager**: `lib/storage/chat_history_manager.py`

**Operations**:
- `load_chat_history(expert_id)` - Load the messages from file (empty list if missing or invalid)
- `save_chat_history(expert_id, messages)` - Save to file (adds timestamps)
- `delete_chat_history(expert_id)` - Delete the file and the expert's images
- `assistant_message(content, provider, model)` - Build an assistant message that records the producing LLM (used for its avatar)
- Enforces 1MB file size limit (`truncate_messages_by_size()` drops the oldest messages, keeping at least 10)

**Persistence Flow**:

```
User sends message
    ↓
Expert page: Generate response
    ↓
Add to session state messages
    ↓
save_chat_history()
    ↓
Write to chat_history/{expert_id}.json
```

**Loading Flow**:

```
User navigates to expert page
    ↓
Expert page: Initialize session state
    ↓
load_chat_history()
    ↓
Read from chat_history/{expert_id}.json
    ↓
Populate st.session_state[f"messages_{expert_id}"]
    ↓
Display conversation in UI
```

### 2. Chat Image Attachments

**Location**: `chat_attachments/{expert_id}/<uuid>.<ext>` (project root, gitignored, local per machine)

**Format**: Original image bytes (PNG, JPEG, WebP, GIF)

**Manager**: `lib/storage/attachment_store.py`

**Operations**:
- `save_image(expert_id, name, data)` - Save an attached image, return its reference (`"{expert_id}/<uuid>.<ext>"`)
- `get_image_path(ref)` - Resolve a reference to a file path (None if invalid or missing)
- `get_image_data_url(ref)` - Base64 data URL for the LLM request
- `delete_expert_attachments(expert_id)` - Delete all images of an expert (called by `delete_chat_history()`)
- All paths go through `safe_path_join()` to prevent path traversal

The chat history only stores an `<image name="..." ref="...">` tag in the user message, not the image itself, so the JSON file stays small and token counting is not distorted. `to_api_content()` (`lib/shared/attachments.py`) loads the images when a request is sent. If an image file is deleted, the message shows "no longer available" and the model receives a short note instead. `scripts/reset_application.py` deletes the whole directory.

### 3. Expert Configurations

**Location**: `configs/{expert_id}.yaml`

**Format**: YAML

**Example**:
```yaml
expert_id: "1001_python_expert"
expert_name: "Python Expert"
description: "Expert in Python programming..."
temperature: 0.7
system_prompt: |
  You are Python Expert...
created_at: "2025-01-17T12:00:00.000000"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

**Manager**: `lib/config/config_manager.py` (`ConfigManager`, use the cached `get_config_manager()`)

**Operations**:
- `create_config(expert_name, description, page_number, ...)` - Create YAML file, returns the expert ID
- `load_config(expert_id)` - Load YAML file
- `update_config(expert_id, updates)` - Update fields (incl. `provider`, `model`, `thinking_level`)
- `delete_config(expert_id)` - Delete YAML file
- `list_experts_lightweight()` - List all experts (without system prompts, cached)
- `get_llm_metadata(config)` - Module function: `(provider, model, thinking_level)` with defaults

### 4. User Preferences

**Location**: `.streamlit/app_defaults.toml`

**Format**: TOML

**Example**:
```toml
[llm]
provider = "deepseek"
model = "deepseek-flash"
thinking_level = "none"

[language]
code = "en"

[display]
git_branch = true
```

**Manager**: `lib/config/app_defaults_manager.py`

**Operations**:
- `get_llm_defaults()` - Get default provider, model and thinking level
- `save_llm_defaults(provider, model, thinking_level)` - Save LLM defaults
- `get_language_preference()` - Get language code
- `save_language_preference(lang_code)` - Save language code
- `get_display_defaults()` - Get display settings (`git_branch`)
- `save_display_setting(key, value)` - Save a display setting

### 5. Theme Settings

**Location**: `.streamlit/config.toml`

**Format**: TOML

**Example**:
```toml
[theme]
base = ".streamlit/themes/dark_gray.toml"
```

The colors live in the referenced theme file under `.streamlit/themes/`.

**Manager**: `lib/config/config_toml_manager.py`

**Operations**:
- `get_theme_settings()` - Load theme settings
- `save_theme_settings(base)` - Save the theme file path (`base`)
- `get_current_theme_name()` / `load_available_themes()` - Current and available themes

## Cache Invalidation

### Config Cache Invalidation

**Purpose**: Force reload of expert config when edited

**Mechanism**: `cache_version_{expert_id}` in session state

**When Config is Edited** (via Settings page, or the toolbox model row on the expert page):

```python
# User edits expert config
get_config_manager().update_config(expert_id=expert_id, updates={...})

# Increment cache version (lib/shared/session_state.py)
invalidate_expert_cache(expert_id)

# Next page load will use new config
```

**In Expert Page** (with caching):

```python
@st.cache_data(ttl=CONFIG_CACHE_TTL, show_spinner="Loading expert configuration...")
def load_expert_config_cached(expert_id: str, cache_version: int = 0) -> dict:
    ...  # get_config_manager().load_config(expert_id)

# Get current cache version
cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)

# Load config (cached if version unchanged)
config = load_expert_config_cached(EXPERT_ID, cache_version)
```

**When Version Changes**:
- Cache invalidated
- Config reloaded from file
- Latest changes reflected

## State Lifecycle

### Application Startup

```
Browser opens app.py
    ↓
Streamlit initializes
    ↓
app.py: Initialize navigation
    ↓
Home page loads (or navigates to last page)
    ↓
initialize_shared_session_state()
    ├─ Load API keys
    ├─ Load defaults
    └─ Initialize language
    ↓
User navigates to expert page
    ↓
Expert page: Initialize per-expert state
    ├─ Load chat history
    ├─ Load expert config (cached)
    └─ Read provider/model/thinking level from config metadata
    ↓
Ready for user interaction
```

### During Session

```
User interacts with expert
    ↓
Update per-expert session state
    └─ Add messages to history
    ↓
Save to persistent storage
    ├─ Save chat history
    └─ Model row changes (provider/model/thinking/temperature) are
       saved to the expert config immediately + invalidate_expert_cache()
    ↓
Update UI
```

### Session End

```
User closes browser tab
    ↓
Session state cleared (Streamlit mechanism)
    ↓
Persistent storage remains
    ├─ Chat history: Saved in files
    ├─ Expert configs: Saved in YAML
    ├─ User preferences: Saved in TOML
    └─ Theme: Saved in TOML
```

### Application Restart

```
User restarts app (F5 or streamlit run app.py)
    ↓
Session state cleared
    ↓
Persistent storage loaded
    ├─ Chat history: Reloaded when expert page loads
    ├─ Expert configs: Used as-is
    ├─ User preferences: Loaded into session state
    └─ Theme: Applied automatically
    ↓
State restored from persistent storage
```

## State Synchronization

### Session State ↔ Persistent Storage

**Chat History Sync**:

```
┌─────────────────────────────────────────────────────────────┐
│  Session State (In-Memory)                                  │
│  st.session_state[f"messages_{expert_id}"]                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
              Load                   Save
                    │                    │
                    ↓                    ↓
┌───────────────────────────────┐  ┌──────────────────────────┐
│  Persistent Storage (Disk)    │  │  Persistent Storage      │
│  chat_history/{expert_id}.json│  │  chat_history/{expert_id}.json│
└───────────────────────────────┘  └──────────────────────────┘
```

**Sync Points**:
1. **Load**: When expert page loads
2. **Save**: After each message exchange
3. **Auto-save**: Triggered by user actions

### Multi-Tab/Window Considerations

**Current Behavior**: Each tab/window has separate session state

**Persistent Storage**: Shared across tabs/windows

**Scenario**:
```
Tab 1: Chat with Python Expert
    ↓
Save to chat_history/1001_python_expert.json
    ↓
Tab 2: Open same expert
    ↓
Load from chat_history/1001_python_expert.json
    ↓
See conversation from Tab 1
```

**Note**: Real-time sync NOT implemented (no websockets)

## Best Practices

### 1. Initialize State Before Use

**Good**:
```python
if f"messages_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"messages_{EXPERT_ID}"] = []
```

**Bad**:
```python
# May raise KeyError if not initialized
messages = st.session_state[f"messages_{EXPERT_ID}"]
```

### 2. Use Explicit Variable Names

**Good**:
```python
st.session_state[f"messages_{EXPERT_ID}"] = []
```

**Bad**:
```python
st.session_state.messages = []  # Not per-expert
```

### 3. Persist Important Data

**Always persist**:
- Chat history (user conversations)
- Expert configs (expert definitions)
- User preferences (defaults)

**Session-only**:
- Temporary UI state
- Navigation history
- Form input state

### 4. Handle Cache Invalidation

**When config changes**:
```python
# Update config
get_config_manager().update_config(expert_id=expert_id, updates=updates)

# Invalidate cache
invalidate_expert_cache(expert_id)
```

### 5. Use Appropriate Storage

**Session State**:
- Temporary data
- UI state
- Current page context

**Persistent Storage**:
- User data (chat history)
- Configuration (expert configs)
- Preferences (defaults, theme)

## Troubleshooting

### Session State Lost on Refresh

**Problem**: Session state cleared when refreshing page

**Explanation**: This is expected Streamlit behavior

**Solution**: Ensure important data persisted to files
- Chat history: Saved to `chat_history/`
- Configs: Saved to `configs/`

### Chat History Not Persisting

**Problem**: Messages not saved across sessions

**Possible Causes**:
1. `save_chat_history()` not called
2. File permission issues
3. Disk full
4. Path issues

**Solution**:
```python
# Verify save is called
save_chat_history(EXPERT_ID, messages)

# Check file exists
ls chat_history/

# Check file permissions
ls -la chat_history/
```

### Config Changes Not Reflected

**Problem**: Edited expert config but old values used

**Cause**: Config cached by `st.cache_data` (keyed by `cache_version_{expert_id}`, TTL `CONFIG_CACHE_TTL` = 300 s)

**Solution**:
```python
# Invalidate cache
invalidate_expert_cache(EXPERT_ID)

# Or restart app
```

### Session State Bloat

**Problem**: App slow, high memory usage

**Cause**: Too much data in session state

**Solution**:
- Persist large data to disk (chat history)
- Keep only essential data in session state
- Clear old messages periodically

## Performance Optimizations

### 1. Lazy Loading

**Load data only when needed**:
```python
# Bad: Load all chat histories at startup
all_histories = {id: load(id) for id in expert_ids}

# Good: Load on demand (the template loads only its own expert's history)
messages = load_chat_history(EXPERT_ID)
```

### 2. Config Caching

**Cache expert configs with TTL**:
```python
@st.cache_data(ttl=CONFIG_CACHE_TTL)  # 300 s = 5 minutes
def load_expert_config_cached(expert_id: str, cache_version: int = 0) -> dict:
    ...
```

## Related Documentation

- **[Architecture Overview](overview.md)** - System architecture
- **[Configuration Overview](../configuration/overview.md)** - Configuration system
- **[Development - Session State](../development/project-structure.md)** - Code structure

---

**Back to**: [Documentation Home](../README.md) | [Architecture Overview](overview.md)
