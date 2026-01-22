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
│  - Provider selection: provider_{expert_id}                 │
│  - Model selection: model_{expert_id}                       │
│  - Temperature: temperature_{expert_id}                     │
│  - Thinking level: thinking_{expert_id}                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. PERSISTENT STORAGE                                      │
│  Survives app restarts                                       │
│  - Chat history: chat_history/{expert_id}.json              │
│  - Expert configs: configs/{expert_id}.yaml                 │
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
# API Keys (loaded from secrets.toml)
st.session_state.api_keys = {
    "deepseek": "sk-...",
    "openai": "sk-...",
    "zai": "..."
}

# Default LLM Settings (loaded from app_defaults.toml)
st.session_state.default_provider = "deepseek"
st.session_state.default_model = "deepseek-chat"
st.session_state.default_temperature = 0.7
st.session_state.default_thinking_level = "none"

# Language Preference (loaded from app_defaults.toml)
st.session_state.language = "en"  # Auto-detected on first run

# Navigation State
st.session_state.navigation_initialized = True
```

**Initialization Flow**:

```
App starts
    ↓
initialize_shared_session_state() called
    ↓
Load API keys from SecretsManager
    ↓
Load defaults from AppDefaultsManager
    ↓
Initialize language (auto-detect or load)
    ↓
Mark initialization complete
```

### 2. Per-Expert Session State

**Purpose**: Expert-specific settings and conversation context

**Lifetime**: Application session (browser tab)

**Initialized By**: Individual expert pages

**State Variables Pattern**:

```python
# For each expert with ID "1001_python_expert"

# Messages History
st.session_state.messages_1001_python_expert = [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
]

# Provider Selection
st.session_state.provider_1001_python_expert = "deepseek"

# Model Selection
st.session_state.model_1001_python_expert = "deepseek-chat"

# Temperature
st.session_state.temperature_1001_python_expert = 0.7

# Thinking Level
st.session_state.thinking_1001_python_expert = "none"

# Cache Version (for invalidation)
st.session_state.cache_version_1001_python_expert = 1
```

**Dynamic Variable Names**:

Using f-strings to create expert-specific keys:

```python
EXPERT_ID = "1001_python_expert"

# Messages history
key = f"messages_{EXPERT_ID}"
if key not in st.session_state:
    st.session_state[key] = []

# Provider selection
key = f"provider_{EXPERT_ID}"
if key not in st.session_state:
    st.session_state[key] = config.get("metadata", {}).get("provider", "deepseek")
```

**Initialization in Expert Pages**:

```python
# pages/1001_python_expert.py

EXPERT_ID = "1001_python_expert"

# Load expert config
config = config_manager.load_config(EXPERT_ID)

# Initialize messages history
if f"messages_{EXPERT_ID}" not in st.session_state:
    # Load from persistent storage
    chat_history = chat_history_manager.load_chat_history(EXPERT_ID)
    st.session_state[f"messages_{EXPERT_ID}"] = chat_history or []

# Initialize provider
if f"provider_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"provider_{EXPERT_ID}"] = config.get("metadata", {}).get("provider", "deepseek")

# Initialize model
if f"model_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"model_{EXPERT_ID}"] = config.get("metadata", {}).get("model", "deepseek-chat")

# Initialize temperature
if f"temperature_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"temperature_{EXPERT_ID}"] = config.get("temperature", 0.7)

# Initialize thinking level
if f"thinking_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"thinking_{EXPERT_ID}"] = config.get("thinking_level", "none")

# Initialize cache version
if f"cache_version_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"cache_version_{EXPERT_ID}"] = 0
```

## Persistent Storage

### 1. Chat History

**Location**: `chat_history/{expert_id}.json`

**Format**: JSON

**Example**:
```json
[
  {
    "role": "user",
    "content": "How do I read a file in Python?"
  },
  {
    "role": "assistant",
    "content": "You can use the open() function..."
  }
]
```

**Manager**: `lib/storage/chat_history_manager.py`

**Operations**:
- `load_chat_history(expert_id)` - Load from file
- `save_chat_history(expert_id, messages)` - Save to file
- Enforces 1MB file size limit

**Persistence Flow**:

```
User sends message
    ↓
Expert page: Generate response
    ↓
Add to session state messages
    ↓
ChatHistoryManager.save_chat_history()
    ↓
Write to chat_history/{expert_id}.json
```

**Loading Flow**:

```
User navigates to expert page
    ↓
Expert page: Initialize session state
    ↓
ChatHistoryManager.load_chat_history()
    ↓
Read from chat_history/{expert_id}.json
    ↓
Populate st.session_state[f"messages_{expert_id}"]
    ↓
Display conversation in UI
```

### 2. Expert Configurations

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
  version: "1.0"
  model: "deepseek-chat"
```

**Manager**: `lib/config/config_manager.py`

**Operations**:
- `load_config(expert_id)` - Load YAML file
- `save_config(expert_id, config)` - Save/update YAML file
- `delete_config(expert_id)` - Delete YAML file
- `list_experts()` - List all expert IDs

### 3. User Preferences

**Location**: `.streamlit/app_defaults.toml`

**Format**: TOML

**Example**:
```toml
[llm]
provider = "deepseek"
model = "deepseek-chat"
temperature = 0.7
thinking_level = "none"

[language]
code = "en"
```

**Manager**: `lib/config/app_defaults_manager.py`

**Operations**:
- `get_provider_preference()` - Get default provider
- `get_model_preference()` - Get default model
- `get_temperature_preference()` - Get default temperature
- `get_thinking_level_preference()` - Get default thinking level
- `get_language_preference()` - Get language code
- `save_provider_preference()` - Save default provider
- `save_language_preference()` - Save language code

### 4. Theme Settings

**Location**: `.streamlit/config.toml`

**Format**: TOML

**Example**:
```toml
[theme]
primaryColor = "#6366F1"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"
```

**Manager**: `lib/config/config_toml_manager.py`

**Operations**:
- `load_theme()` - Load theme settings
- `save_theme(theme_dict)` - Save theme settings

## Cache Invalidation

### Config Cache Invalidation

**Purpose**: Force reload of expert config when edited

**Mechanism**: `cache_version_{expert_id}` in session state

**When Config is Edited** (via Settings page):

```python
# User edits expert config
config_manager.update_config(expert_id, new_config)

# Increment cache version
st.session_state[f"cache_version_{expert_id}"] += 1

# Next page load will use new config
```

**In Expert Page** (with caching):

```python
@st.cache_data(ttl=300)
def load_config_with_cache(expert_id, cache_version):
    return config_manager.load_config(expert_id)

# Get current cache version
cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)

# Load config (cached if version unchanged)
config = load_config_with_cache(EXPERT_ID, cache_version)
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
    ├─ Load expert config
    ├─ Load chat history
    └─ Initialize provider/model/temperature
    ↓
Ready for user interaction
```

### During Session

```
User interacts with expert
    ↓
Update per-expert session state
    ├─ Add messages to history
    ├─ Update provider/model selection
    └─ Update temperature/thinking
    ↓
Save to persistent storage
    ├─ Save chat history
    └─ (Config changes saved separately)
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
st.session_state[f"provider_{EXPERT_ID}"] = "deepseek"
```

**Bad**:
```python
st.session_state.provider = "deepseek"  # Not per-expert
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
config_manager.update_config(expert_id, new_config)

# Invalidate cache
st.session_state[f"cache_version_{expert_id}"] += 1
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
chat_history_manager.save_chat_history(EXPERT_ID, messages)

# Check file exists
ls chat_history/

# Check file permissions
ls -la chat_history/
```

### Config Changes Not Reflected

**Problem**: Edited expert config but old values used

**Cause**: Config cached in session state

**Solution**:
```python
# Invalidate cache
st.session_state[f"cache_version_{EXPERT_ID}"] += 1

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

# Good: Load on demand
def get_chat_history(expert_id):
    return chat_history_manager.load_chat_history(expert_id)
```

### 2. Config Caching

**Cache expert configs with TTL**:
```python
@st.cache_data(ttl=300)  # 5 minutes
def load_config_cached(expert_id):
    return config_manager.load_config(expert_id)
```

### 3. Efficient State Updates

**Batch updates**:
```python
# Bad: Multiple writes
save_chat_history(expert_id, messages)
save_config(expert_id, config)

# Good: Single write (if related)
save_all(expert_id, messages, config)
```

## Related Documentation

- **[Architecture Overview](overview.md)** - System architecture
- **[Configuration Overview](../configuration/overview.md)** - Configuration system
- **[Development - Session State](../development/project-structure.md)** - Code structure

---

**Back to**: [Documentation Home](../README.md) | [Architecture Overview](overview.md)
