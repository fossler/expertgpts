# Architecture Overview

This guide provides a high-level overview of ExpertGPTs' architecture, component organization, and design principles.

## System Architecture

ExpertGPTs is a **multi-expert AI chat application** built with Streamlit, featuring a template-based page generation system and multi-provider LLM integration.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Streamlit Web App)                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                      Navigation Layer                            │
│                   (st.navigation() API)                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ Home Page   │  │Expert Pages  │  │ Settings & Help Pages    │   │
│  │ (1000_)     │  │  (1001-9997) │  │  (9998_, 9999_)          │   │
│  └─────────────┘  └──────────────┘  └──────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                    Business Logic Layer                         │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐  │
│  │Page Generator│  │Config Manager │  │  Chat History Mgr  │  │
│  └──────────────┘  └───────────────┘  └────────────────────┘  │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐  │
│  │  LLM Client  │  │Client Pool    │  │  Secrets Manager   │  │
│  └──────────────┘  └───────────────┘  └────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                    Data Layer                                   │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐  │
│  │Expert Configs│  │Chat History   │  │ User Preferences   │  │
│  │ (YAML files) │  │ (JSON files)  │  │   (TOML files)     │  │
│  └──────────────┘  └───────────────┘  └────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                  External Services                               │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐  │
│  │  DeepSeek    │  │    OpenAI     │  │      Z.AI          │  │
│  │     API      │  │      API      │  │       API          │  │
│  └──────────────┘  └───────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
expertgpts/
├── app.py                          # Main entry point with st.navigation()
├── pages/                          # Streamlit pages
│   ├── 1000_Home.py                # Home page (permanent)
│   ├── 1001_python_expert.py       # Expert pages (generated)
│   ├── 1002_data_scientist.py      # More expert pages...
│   ├── 9998_Settings.py            # Settings page (permanent)
│   └── 9999_Help.py                # Help page (permanent)
├── templates/
│   └── template.py                 # Master template for expert pages
├── configs/                        # Expert configurations
│   ├── 1001_python_expert.yaml
│   ├── 1002_data_scientist.yaml
│   └── ...
├── utils/                          # Shared utilities
│   ├── llm_client.py               # Multi-provider LLM client
│   ├── client_pool.py              # Connection pooling
│   ├── config_manager.py           # Config file operations
│   ├── page_generator.py           # Page generation logic
│   ├── secrets_manager.py          # Secrets management
│   ├── chat_history_manager.py     # Chat history persistence
│   ├── session_state.py            # Session state initialization
│   ├── i18n.py                     # Internationalization
│   └── helpers.py                  # Utility functions
├── locales/                        # UI translations
│   └── ui/
│       ├── en.json                 # English (source of truth)
│       ├── de.json                 # German
│       └── ... (13 language files)
├── chat_history/                   # Conversation storage
│   ├── 1001_python_expert.json
│   └── ...
├── .streamlit/                     # Streamlit configuration
│   ├── secrets.toml                # API keys (gitignored)
│   ├── config.toml                 # Theme settings (gitignored)
│   └── app_defaults.toml           # User preferences (gitignored)
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
└── scripts/                        # Administrative scripts
    ├── setup.py                    # Initial setup
    ├── reset_application.py        # Reset to factory defaults
    ├── update_translations.py      # Sync locales
    └── run_tests.sh                # Run test suite
```

## Core Components

### 1. Navigation System (`app.py`)

**Technology**: Streamlit's `st.navigation()` API

**Purpose**: Centralized routing and page management

**Key Features**:
- Modern Material Design icons
- Dynamic page discovery
- Explicit page ordering (1000-9999, with experts in 1001-9997 range)
- Clean separation of navigation logic

**Page Numbering**:
- **1000**: Home page
- **1001-9997**: Expert pages
- **9998**: Settings page
- **9999**: Help page

### 2. Template System (`templates/template.py`)

**Purpose**: Single source of truth for expert page UI/UX

**Mechanism**:
1. Template contains placeholders: `{{EXPERT_ID}}`, `{{EXPERT_NAME}}`
2. PageGenerator replaces placeholders with expert-specific values
3. Generates complete Python page files

**Benefits**:
- DRY principle (update once, apply to all)
- Consistent UI across all experts
- Easy to add new features to all expert pages

**See also**: [Template System Guide](template-system.md)

### 3. Multi-Provider LLM Client (`lib/llm/llm_client.py`)

**Purpose**: Unified interface for multiple LLM providers

**Supported Providers**:
- DeepSeek (default)
- OpenAI
- Z.AI

**Architecture**:
- OpenAI Python client with custom `base_url`
- Provider-specific thinking parameter handling
- Connection pooling via `client_pool.py`

**Key Innovation**: `_prepare_thinking_param()` method handles provider differences:
- OpenAI: `reasoning_effort` (low/medium/high)
- DeepSeek: `thinking.type` (model-dependent)
- Z.AI: `thinking.type` (via extra_body)

**See also**: [Multi-Provider LLM Guide](multi-provider-llm.md)

### 4. Configuration Management (`lib/config/config_manager.py`)

**Purpose**: Manage expert YAML configurations

**Operations**:
- Load expert config by ID
- Save/update expert config
- Delete expert config
- List all experts

**Config Storage**: `configs/{expert_id}.yaml`

**See also**: [Configuration Guide](../configuration/expert-configs.md)

### 5. Page Generator (`lib/shared/page_generator.py`)

**Purpose**: Generate new expert pages from template

**Process**:
1. Generate unique expert ID
2. Create YAML config
3. Generate page file from template
4. Register with navigation system

**Auto-Navigation**: Automatically navigates to new expert after creation

### 6. Internationalization (`lib/i18n/i18n.py`)

**Purpose**: Multi-language support (13 languages)

**Three-Layer Architecture**:

```
┌─────────────────────────────────────────────────────────┐
│  1. STORAGE LAYER (configs/*.yaml)                      │
│  Expert content in English - Single Source of Truth     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  2. TRANSLATION LAYER (locales/ui/*.json)               │
│  UI translations ONLY - Buttons, labels, messages       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  3. RUNTIME LAYER (template.py, i18n.py)                │
│  Language prefix injection: "Respond in German"         │
└─────────────────────────────────────────────────────────┘
```

**Key Feature**: Language prefix injected at runtime ensures AI responds in user's selected language.

**See also**: [Internationalization Guide](../internationalization/I18N_GUIDE.md)

### 7. Session State Management (`lib/shared/session_state.py`)

**Purpose**: Initialize and manage session state

**State Types**:

**Shared Session State**:
- API keys for all providers
- Default LLM settings
- Language preference
- Navigation state

**Per-Expert Session State**:
- Messages history
- Provider selection
- Model selection
- Temperature
- Thinking level

**See also**: [State Management Guide](state-management.md)

### 8. Chat History Manager (`lib/storage/chat_history_manager.py`)

**Purpose**: Persistent conversation storage

**Storage**: `chat_history/{expert_id}.json`

**Features**:
- 1MB file size limit per expert
- Auto-trimming when limit exceeded
- Load/save operations

## Data Flow

### Creating a New Expert

```
User clicks "Add Chat"
    ↓
Home page: Display creation form
    ↓
User submits form (name, description, temperature, etc.)
    ↓
PageGenerator.generate_page()
    ├─ Generate expert ID
    ├─ Create YAML config (configs/{expert_id}.yaml)
    ├─ Generate page from template (pages/{expert_id}.py)
    └─ Return expert ID
    ↓
st.navigation() navigates to new expert page
    ↓
Expert page loads (session state initialized)
```

### Chat Interaction

```
User enters message
    ↓
Expert page: Capture input
    ↓
Load chat history (if any)
    ↓
Inject language prefix (runtime i18n)
    ↓
Construct system prompt
    ↓
LLMClient.generate_response()
    ├─ Get cached client (client_pool.py)
    ├─ Prepare thinking parameters (provider-specific)
    ├─ Call LLM API (DeepSeek/OpenAI/Z.AI)
    └─ Return response
    ↓
Display response to user
    ↓
ChatHistoryManager.save_chat_history()
    ↓
Update session state
```

### Expert Page Load

```
User navigates to expert page
    ↓
Streamlit loads expert page (pages/{expert_id}.py)
    ↓
Initialize per-expert session state
    ├─ Load expert config (configs/{expert_id}.yaml)
    ├─ Load chat history (chat_history/{expert_id}.json)
    └─ Initialize provider/model settings
    ↓
Render expert interface
    ├─ Display chat history
    ├─ Show provider/model controls
    └─ Display chat input
```

## Design Principles

### 1. DRY (Don't Repeat Yourself)

**Applied to**:
- **Expert pages**: Single template for all experts
- **Configuration**: Centralized in YAML files
- **Utilities**: Shared functions in `lib/`
- **i18n**: Single source of truth for expert content

### 2. Separation of Concerns

**Layers**:
- **UI Layer**: Streamlit pages (presentation)
- **Business Logic**: Utility modules (processing)
- **Data Layer**: YAML/JSON files (persistence)

### 3. Template-Based Generation

**Benefits**:
- Consistent UI/UX across experts
- Easy to add features (update template, regenerate)
- Reduces code duplication
- Maintainable architecture

### 4. Multi-Provider Abstraction

**Implementation**:
- Unified `LLMClient` interface
- Provider-specific parameter handling
- Connection pooling for performance
- Easy to add new providers

### 5. Single Source of Truth

**Examples**:
- **Expert content**: YAML configs (not locale files)
- **UI translations**: `en.json` (synced to all languages)
- **Expert pages**: Single template file
- **Navigation**: Centralized in `app.py`

## Technology Stack

### Frontend
- **Framework**: Streamlit
- **Language**: Python
- **Icons**: Material Design (via Streamlit)

### Backend
- **Language**: Python 3.8+
- **LLM Clients**: OpenAI Python SDK
- **Data Formats**: YAML, JSON, TOML

### External Services
- **LLM Providers**: DeepSeek, OpenAI, Z.AI
- **APIs**: OpenAI-compatible endpoints

### Development
- **Testing**: pytest
- **Code Quality**: Black (formatter)
- **Version Control**: Git

## Performance Optimizations

### 1. Connection Pooling

**File**: `lib/llm/client_pool.py`

**Purpose**: Cache LLM client instances

**Benefit**: ~50% reduction in client creation overhead

### 2. Configuration Caching

**Implementation**: `@st.cache_data(ttl=CONFIG_CACHE_TTL)`

**Benefit**: Faster expert page loads

### 3. Lazy Page Loading

**Mechanism**: Streamlit loads only active page

**Benefit**: Faster app startup, lower memory usage

### 4. Pre-computed Lookup Tables

**File**: `lib/shared/constants.py`

**Purpose**: O(1) provider/model lookups

**Benefit**: Eliminates nested dict access overhead

## Security Considerations

### 1. API Key Management

- Stored in `.streamlit/secrets.toml` (gitignored)
- File permissions: 600 (owner read/write only)
- Access via Streamlit secrets API only

### 2. Input Validation

- Expert names: Sanitized to prevent path traversal
- API keys: Minimum 20 characters, format validation
- Temperature: Range validation (0.0-2.0)

### 3. File Permissions

- Secrets file: 600 permissions
- Automatic permission setting on save
- Verification on load

## Scalability

### Horizontal Scaling

**Current**: Single-instance deployment

**Future Considerations**:
- Shared storage for configs and chat history
- Session state management (Redis)
- Load balancing

### Vertical Scaling

**Optimizations**:
- Connection pooling (reduces overhead)
- Configuration caching (reduces I/O)
- Lazy loading (reduces memory)

## Extensibility

### Adding New LLM Providers

**Steps**:
1. Add provider configuration to `lib/shared/constants.py`
2. Update `_prepare_thinking_param()` in `llm_client.py`
3. Add API key UI in Settings page
4. Update secrets template

**Estimated Effort**: ~1 hour

### Adding New Expert Features

**Steps**:
1. Update `templates/template.py`
2. Run `reset_application.py` to regenerate pages
3. Update configuration schema if needed

**Estimated Effort**: Depends on feature

### Adding New Languages

**Steps**:
1. Add language metadata to `lib/i18n/i18n.py`
2. Create locale file: `locales/ui/{code}.json`
3. Add language names to all locale files
4. Test with `update_translations.py`

**Estimated Effort**: ~2 hours

## Next Steps

- **[Template System Guide](template-system.md)** - Template-based page generation
- **[Multi-Provider LLM Guide](multi-provider-llm.md)** - LLM provider integration
- **[State Management Guide](state-management.md)** - Session state and persistence
- **[Development Setup Guide](../development/setup.md)** - Development environment

---

**Back to**: [Documentation Home](../README.md)
