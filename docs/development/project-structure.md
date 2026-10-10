# Project Structure

This guide explains the ExpertGPTs project structure and file organization.

## Directory Tree

```
expertgpts/
├── app.py                          # Main entry point with st.navigation()
├── CLAUDE.md                       # Project instructions for AI
├── README.md                       # Project overview and quick start
│
├── pages/                          # Streamlit pages
│   ├── 1000_Home.py               # Home page (permanent, committed)
│   ├── 1001_python_expert.py      # Expert pages (generated)
│   ├── 1002_data_scientist.py     # More expert pages...
│   ├── 9998_Settings.py           # Settings page (permanent, committed)
│   ├── 9999_Help.py               # Help page (permanent, committed)
│   └── _debug.py                  # Debug page at /debug (permanent, hidden from navigation)
│
├── templates/
│   └── template.py                 # Master template for expert pages
│
├── configs/                        # Expert configurations (YAML, gitignored)
│   ├── 1001_python_expert.yaml
│   ├── 1002_data_scientist.yaml
│   └── ...
│
├── lib/                            # Core library (domain-driven structure)
│   ├── llm/                       # LLM-related modules
│   │   ├── llm_client.py          # Multi-provider LLM client
│   │   ├── client_pool.py         # Connection pooling
│   │   └── token_manager.py       # Token counting and context management
│   ├── audio/                     # Audio processing
│   │   └── transcription.py       # Speech-to-text for voice input
│   ├── config/                    # Configuration management
│   │   ├── config_manager.py      # Expert config operations
│   │   ├── secrets_manager.py     # API key management
│   │   ├── app_defaults_manager.py # User preferences
│   │   └── config_toml_manager.py # Theme configuration
│   ├── i18n/                      # Internationalization
│   │   └── i18n.py                # Language detection and translation
│   ├── storage/                   # Data persistence
│   │   ├── chat_history_manager.py # Chat history persistence
│   │   ├── attachment_store.py    # Chat image files (chat_attachments/)
│   │   └── streaming_cache.py     # Background response caching
│   ├── ui/                        # UI components
│   │   ├── chat_toolbox.py        # Toolbox below the chat input (attach file/image, context usage)
│   │   └── dialogs.py             # Shared dialog rendering
│   └── shared/                    # Shared utilities
│       ├── attachments.py         # Text file and image attachments in chat messages
│       ├── constants.py           # Provider/model configurations
│       ├── file_ops.py            # File system operations
│       ├── format_ops.py          # File format operations (TOML, YAML, JSON)
│       ├── helpers.py             # Utility functions
│       ├── page_generator.py      # Expert page generation
│       ├── session_state.py       # Session state initialization
│       └── types.py               # Type definitions
│
├── locales/                        # UI translations
│   └── ui/
│       ├── en.json                 # English (source of truth)
│       ├── de.json                 # German
│       ├── es.json                 # Spanish
│       └── ... (14 language files)
│
├── chat_history/                   # Conversation storage (JSON, gitignored)
│   ├── 1001_python_expert.json
│   └── ...
│
├── chat_attachments/               # Images attached in the chat (gitignored)
│   ├── 1001_python_expert/
│   └── ...
│
├── streaming_cache/                # Background streaming cache files (gitignored)
│
├── .streamlit/                     # Streamlit configuration
│   ├── secrets.toml               # API keys (gitignored)
│   ├── secrets.toml.example       # Template for secrets
│   ├── config.toml                # Theme settings (gitignored)
│   ├── config.toml.example        # Template for theme
│   ├── app_defaults.toml          # User preferences (gitignored)
│   ├── app_defaults.toml.example  # Template for defaults
│   └── themes/                    # Predefined theme files (*.toml)
│
├── tests/                          # Test suite
│   ├── README.md
│   ├── test_agent_generation.py
│   ├── test_attachments.py
│   ├── test_i18n.py
│   ├── test_llm_params.py
│   ├── test_message_origin.py
│   ├── test_page_regeneration.py
│   ├── test_streaming_cache.py
│   └── test_transcription.py
│
├── scripts/                        # Administrative scripts
│   ├── setup.py                   # Create example experts
│   ├── regenerate_pages.py        # Regenerate expert pages from template (keeps data)
│   ├── reset_application.py       # Reset to factory defaults (deletes all data)
│   ├── update_translations.py     # Sync locale files
│   ├── benchmark_zai.py           # Z.AI performance benchmark
│   └── run_tests.sh               # Run test suite
│
├── docs/                           # Detailed documentation
│   ├── README.md
│   ├── performance-optimization.md
│   ├── assets/
│   ├── getting-started/
│   ├── user-guide/
│   ├── configuration/
│   ├── architecture/
│   ├── internationalization/
│   ├── development/
│   ├── reference/
│   └── api/
│
├── pyproject.toml                  # Project metadata, dependencies and pytest config
├── uv.lock                         # Locked dependency versions
├── ruff.toml                       # Ruff formatter configuration
└── .gitignore                      # Git ignore patterns
```

## lib/ Domain-Driven Structure

The `lib/` directory is organized into 7 domain-specific subdirectories to group related functionality and improve code discoverability.

### `lib/llm/` - LLM Operations
**Purpose**: All LLM provider interactions, client management, and token tracking.

**When to use**: Adding new LLM providers, modifying client behavior, implementing token counting strategies.

**Modules**:
- `llm_client.py` - Multi-provider LLM client (DeepSeek, OpenAI, Z.AI, KIMI)
- `client_pool.py` - Connection pooling for performance
- `token_manager.py` - Token counting and context usage tracking

**Imports**:
```python
from lib.llm import LLMClient, TokenManager, get_cached_client
```

### `lib/audio/` - Audio Processing
**Purpose**: Speech-to-text for the "Voice input" entry of the chat toolbox.

**When to use**: Changing transcription providers/models or audio limits.

**Modules**:
- `transcription.py` - Transcription via the OpenAI-compatible `/audio/transcriptions` endpoint (OpenAI experts → `gpt-transcribe`, all others → Z.AI `glm-asr-2512`)

**Imports**:
```python
from lib.audio import transcribe, get_transcription_provider, TranscriptionResult
```

### `lib/config/` - Configuration Management
**Purpose**: Expert configurations, API keys, user preferences, and theme settings.

**When to use**: Adding new configuration options, managing secrets, updating app defaults.

**Modules**:
- `config_manager.py` - Expert YAML config CRUD operations
- `secrets_manager.py` - API key storage in `.streamlit/secrets.toml`
- `app_defaults_manager.py` - User preferences (provider, model, language)
- `config_toml_manager.py` - Theme configuration management

**Imports**:
```python
from lib.config import ConfigManager
from lib.config import secrets_manager, config_toml_manager
```

### `lib/i18n/` - Internationalization
**Purpose**: Language detection, translations, and locale management.

**When to use**: Adding new languages, modifying translation behavior, updating locale handling.

**Modules**:
- `i18n.py` - Language detection, locale loading, language prefix injection

**Imports**:
```python
from lib.i18n import i18n, I18nManager
```

### `lib/storage/` - Data Persistence
**Purpose**: Long-term and short-term data storage (chat history, chat images, caching).

**When to use**: Adding new persistence mechanisms, modifying storage backends, implementing caching strategies.

**Modules**:
- `chat_history_manager.py` - Chat conversation persistence (JSON files); `delete_chat_history()` also deletes the expert's images
- `attachment_store.py` - Image attachments on disk under `chat_attachments/{expert_id}/` (save, resolve, base64 data URL, delete per expert; path-traversal safe)
- `streaming_cache.py` - Background streaming response caching

**Imports**:
```python
from lib.storage import load_chat_history, save_chat_history, StreamingCache
```

### `lib/ui/` - UI Components
**Purpose**: Shared UI rendering functions, dialogs, and interactive components.

**When to use**: Adding new dialog types, creating reusable UI components, modifying shared rendering logic.

**Modules**:
- `chat_toolbox.py` - Toolbox row below the chat input ("Attach file", "Attach image", context usage popover on the right) and rendering of user messages with image thumbnails and text attachments
- `dialogs.py` - Add Chat dialog (`open_add_chat_dialog()`, a blocking `st.dialog` modal that closes only via its own buttons), expert creation (`create_new_expert()`) and shared LLM configuration widgets. The Edit, Delete and Reset dialogs live in `pages/9998_Settings.py` (`open_edit_expert_dialog()`, `open_delete_expert_dialog()`, `open_reset_dialog()`)

**Imports**:
```python
from lib.ui import open_add_chat_dialog, render_llm_configuration
```

### `lib/shared/` - Shared Utilities
**Purpose**: Cross-cutting utilities used by multiple domains (constants, file ops, helpers).

**When to use**:
- Adding application-wide constants
- Creating reusable helper functions
- Implementing shared file operations
- Defining types and interfaces

**Modules**:
- `attachments.py` - Text file and image attachments: read/validate uploads, embed text files and image references into the user message, split them out for display, convert stored content for the LLM request (`to_api_content()`)
- `constants.py` - Provider/model configurations, thresholds, lookup tables
- `file_ops.py` - File system operations (permissions, paths, directories)
- `format_ops.py` - File format operations (TOML, YAML, JSON)
- `helpers.py` - Utility functions (name sanitization, translation)
- `page_generator.py` - Expert page generation from template
- `session_state.py` - Session state initialization and management
- `types.py` - Type definitions and dataclasses

**Imports**:
```python
from lib.shared import LLM_PROVIDERS, sanitize_name, PageGenerator
from lib.shared.constants import get_provider_config, get_model_config
```

## When to Create a New Domain

The current 7-domain structure covers most use cases. Consider adding a new domain (e.g., `lib/api/`, `lib/monitoring/`) when:

1. **You're adding a major new capability** with 3+ related modules
2. **The modules have clear interdependencies** but minimal dependencies on other domains
3. **The functionality is conceptually distinct** from existing domains

**Example**: If you were adding a REST API layer with endpoints, authentication, and rate limiting, create `lib/api/` instead of putting everything in `lib/shared/`.

**Guideline**: Start with `lib/shared/` for new utilities. Only create a new domain when you have 3+ related modules that form a coherent subsystem.

## File Types

### Permanent Files (Committed to Git)

**Always committed**:
- `app.py` - Main entry point
- `pages/1000_Home.py` - Home page
- `pages/9998_Settings.py` - Settings page
- `pages/9999_Help.py` - Help page
- `pages/_debug.py` - Debug page
- `templates/template.py` - Expert page template
- `lib/**/*.py` - All library modules
- `tests/*.py` - Test files
- `locales/ui/*.json` - UI translations
- `scripts/*.py` - Administrative scripts
- `.streamlit/*.example` - Template files
- `pyproject.toml`, `uv.lock` - Dependencies
- `CLAUDE.md` - Project instructions
- `README.md` - Project overview
- `docs/**` - Documentation

### Generated Files (Typically Gitignored)

**Auto-generated**:
- `pages/1001_*.py` and higher - Expert pages (generated from template)
- `configs/*.yaml` - Expert configurations (created by `scripts/setup.py` or the UI)

### User-Specific Files (Gitignored)

**Never committed**:
- `.streamlit/secrets.toml` - API keys
- `.streamlit/config.toml` - Theme settings
- `.streamlit/app_defaults.toml` - User preferences
- `chat_history/*.json` - Conversation history
- `chat_attachments/` - Images attached in the chat
- `streaming_cache/` - Background streaming cache

## File Purposes

### Core Application Files

**app.py**:
- Main entry point
- Uses `st.navigation()` for routing
- Initializes shared session state
- Discovers and registers pages

**pages/**:
- Home: Expert management UI
- Expert pages: Generated from template
- Settings: Configuration UI
- Help: Documentation and links
- Debug (`_debug.py`): Diagnostics (environment, dependencies, app health, session state) at `/debug`

### Business Logic Files

**lib/llm/llm_client.py**:
- Multi-provider LLM client
- Handles provider-specific parameters
- Manages API calls

**lib/llm/client_pool.py**:
- Caches LLM client instances
- Performance optimization

**lib/config/config_manager.py**:
- CRUD operations for expert configs
- YAML file operations

**lib/shared/page_generator.py**:
- Generates new expert pages
- Creates unique expert IDs
- Replaces template placeholders

**lib/shared/file_ops.py**:
- Shared file system operations
- Secure permission management (600)
- Path resolution utilities
- File/directory creation helpers

**lib/shared/format_ops.py**:
- Shared file format operations
- TOML read/write with error handling
- YAML read/write for configs
- JSON read/write for chat history

### Configuration Files

**configs/*.yaml**:
- Expert definitions
- Name, description, temperature
- System prompts

**locales/ui/*.json**:
- UI translations only
- Buttons, labels, messages

**.streamlit/secrets.toml**:
- API keys for all providers
- Secure file (600 permissions)

**.streamlit/app_defaults.toml**:
- Default provider/model
- Language preference

**.streamlit/config.toml**:
- Theme customization
- Colors, fonts

## Naming Conventions

### Expert IDs

**Format**: `{number}_{sanitized_name}`

**Examples**:
- `1001_python_expert`
- `1005_sql_expert`
- `1010_career_coach`

**Sanitization**:
- Lowercase
- Spaces/hyphens → underscores
- Alphanumeric + underscores only

### Page Numbers

- **1000**: Home page
- **1001+**: Expert pages
- **9998**: Settings page
- **9999**: Help page

### Config Files

**Format**: `{expert_id}.yaml`

**Matches page**: Expert page `pages/{expert_id}.py`

### Chat History Files

**Format**: `{expert_id}.json`

**Location**: `chat_history/`

### Chat Attachment Files

**Format**: `{expert_id}/<uuid>.<ext>` (PNG, JPEG, WebP, GIF)

**Location**: `chat_attachments/` (referenced from the chat history by `<image ... ref="...">` tags)

## Import Structure

### Utility Module Imports

**In expert pages**:
```python
from lib.config.config_manager import get_config_manager
from lib.llm import LLMClient
from lib.storage import load_chat_history, save_chat_history
from lib.i18n import i18n
```

### Circular Import Prevention

**Utilities typically import**:
- Standard library modules
- Other utilities (avoiding cycles)
- Streamlit components

**Utilities typically don't import**:
- Pages (avoids cycles)
- Templates (avoids cycles)

## File Ownership

### User-Owned Files

**Users create/manage**:
- Expert configs (`configs/*.yaml`)
- Chat history (`chat_history/*.json`)
- Chat images (`chat_attachments/`)
- App defaults (`.streamlit/app_defaults.toml`)
- Theme settings (`.streamlit/config.toml`)

### Application-Owned Files

**Application manages**:
- Expert pages (generated from template)
- Template (`templates/template.py`)
- Library modules (`lib/**/*.py`)

## Permissions

### Secure Files (600)

**Owner read/write only**:
- `.streamlit/secrets.toml` - API keys
- `.streamlit/config.toml` - Theme settings
- `.streamlit/app_defaults.toml` - User preferences

### World-Readable Files (644)

**Committed to git**:
- Application code
- Documentation
- Example files

## Related Documentation

- **[Architecture Overview](../architecture/overview.md)** - System architecture
- **[Development Setup](setup.md)** - Development environment
- **[Adding Features](adding-features.md)** - Feature development

---

**Back to**: [Documentation Home](../README.md) | [Development Setup](setup.md)
