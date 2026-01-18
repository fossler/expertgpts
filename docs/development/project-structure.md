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
│   └── 9999_Help.py               # Help page (permanent, committed)
│
├── templates/
│   └── template.py                 # Master template for expert pages
│
├── configs/                        # Expert configurations (YAML)
│   ├── 1001_python_expert.yaml
│   ├── 1002_data_scientist.yaml
│   └── ...
│
├── utils/                          # Shared utilities and business logic
│   ├── llm_client.py              # Multi-provider LLM client
│   ├── client_pool.py             # Connection pooling
│   ├── config_manager.py          # Expert config operations
│   ├── page_generator.py          # Expert page generation
│   ├── secrets_manager.py         # API key management
│   ├── config_toml_manager.py     # Theme configuration
│   ├── app_defaults_manager.py    # User preferences
│   ├── chat_history_manager.py    # Chat history persistence
│   ├── session_state.py           # Session state initialization
│   ├── token_manager.py           # Token counting
│   ├── i18n.py                    # Internationalization
│   ├── constants.py               # Provider/model configurations
│   ├── helpers.py                 # Utility functions
│   ├── file_ops.py                # File system operations (NEW)
│   └── format_ops.py              # File format operations (NEW)
│
├── locales/                        # UI translations
│   └── ui/
│       ├── en.json                 # English (source of truth)
│       ├── de.json                 # German
│       ├── es.json                 # Spanish
│       └── ... (13 language files)
│
├── chat_history/                   # Conversation storage (JSON)
│   ├── 1001_python_expert.json
│   └── ...
│
├── .streamlit/                     # Streamlit configuration
│   ├── secrets.toml               # API keys (gitignored)
│   ├── secrets.toml.example       # Template for secrets
│   ├── config.toml                # Theme settings (gitignored)
│   ├── config.toml.example        # Template for theme
│   ├── app_defaults.toml          # User preferences (gitignored)
│   └── app_defaults.toml.example  # Template for defaults
│
├── tests/                          # Test suite
│   ├── test_agent_generation.py
│   └── test_i18n.py
│
├── scripts/                        # Administrative scripts
│   ├── setup.py                   # Create example experts
│   ├── reset_application.py       # Regenerate expert pages
│   ├── update_translations.py     # Sync locale files
│   └── run_tests.sh               # Run test suite
│
├── docs/                           # Detailed documentation
│   ├── README.md
│   ├── getting-started/
│   ├── user-guide/
│   ├── configuration/
│   ├── architecture/
│   ├── internationalization/
│   ├── development/
│   ├── reference/
│   └── api/
│
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
└── .gitignore                      # Git ignore patterns
```

## File Types

### Permanent Files (Committed to Git)

**Always committed**:
- `app.py` - Main entry point
- `pages/1000_Home.py` - Home page
- `pages/9998_Settings.py` - Settings page
- `pages/9999_Help.py` - Help page
- `templates/template.py` - Expert page template
- `utils/*.py` - All utility modules
- `configs/*.yaml` - Expert configurations
- `tests/*.py` - Test files
- `locales/ui/*.json` - UI translations
- `scripts/*.py` - Administrative scripts
- `.streamlit/*.example` - Template files
- `requirements*.txt` - Dependencies
- `CLAUDE.md` - Project instructions
- `README.md` - Project overview
- `docs/**` - Documentation

### Generated Files (Typically Gitignored)

**Auto-generated**:
- `pages/1001_*.py` to `pages/9998_*.py` - Expert pages (generated from template)

### User-Specific Files (Gitignored)

**Never committed**:
- `.streamlit/secrets.toml` - API keys
- `.streamlit/config.toml` - Theme settings
- `.streamlit/app_defaults.toml` - User preferences
- `chat_history/*.json` - Conversation history

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

### Business Logic Files

**utils/llm_client.py**:
- Multi-provider LLM client
- Handles provider-specific parameters
- Manages API calls

**utils/client_pool.py**:
- Caches LLM client instances
- Performance optimization

**utils/config_manager.py**:
- CRUD operations for expert configs
- YAML file operations

**utils/page_generator.py**:
- Generates new expert pages
- Creates unique expert IDs
- Replaces template placeholders

**utils/file_ops.py**:
- Shared file system operations
- Secure permission management (600)
- Path resolution utilities
- File/directory creation helpers

**utils/format_ops.py**:
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
- **1001-9998**: Expert pages
- **9999**: Settings page

### Config Files

**Format**: `{expert_id}.yaml`

**Matches page**: Expert page `pages/{expert_id}.py`

### Chat History Files

**Format**: `{expert_id}.json`

**Location**: `chat_history/`

## Import Structure

### Utility Module Imports

**In expert pages**:
```python
from utils.config_manager import ConfigManager
from utils.llm_client import LLMClient
from utils.chat_history_manager import ChatHistoryManager
from utils.i18n import i18n
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
- App defaults (`.streamlit/app_defaults.toml`)
- Theme settings (`.streamlit/config.toml`)

### Application-Owned Files

**Application manages**:
- Expert pages (generated from template)
- Template (`templates/template.py`)
- Utilities (`utils/*.py`)

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
