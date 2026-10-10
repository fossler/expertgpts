# Configuration System Overview

This guide explains ExpertGPTs' configuration system, including file types, locations, and how settings are managed.

## Configuration Architecture

ExpertGPTs uses a **multi-layered configuration system** with different files for different purposes:

```
┌─────────────────────────────────────────────────────────────┐
│  1. EXPERT CONFIGS                                          │
│  Location: configs/*.yaml                                   │
│  Purpose: Individual expert definitions                     │
│  Managed: Via UI or manually                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. USER PREFERENCES                                        │
│  Location: .streamlit/app_defaults.toml                     │
│  Purpose: Default provider, model, language, display        │
│  Managed: Via Settings page                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. THEME SETTINGS                                          │
│  Location: .streamlit/config.toml                           │
│  Purpose: UI theme (base = theme file), client settings     │
│  Managed: Via Settings page                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. API KEYS                                                │
│  Location: .streamlit/secrets.toml                          │
│  Purpose: API keys for LLM providers                        │
│  Managed: Via Settings page (recommended)                   │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Files

### 1. Expert Configurations (`configs/*.yaml`)

**Purpose**: Define individual expert agents

**Location**: `configs/` directory in project root

**Format**: YAML

**Example**:
```yaml
expert_id: "1001_python_expert"
expert_name: "Python Expert"
description: "Expert in Python programming, software development, debugging, and best practices"
temperature: 0.7
system_prompt: |
  You are Python Expert, a domain-specific expert AI assistant...
created_at: "2025-01-17T12:00:00.123456"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "high"
```

**Naming Convention**: `{expert_id}.yaml`

**Management**:
- Created automatically when adding experts via UI
- Model, thinking level and temperature are saved immediately when changed in the chat toolbox
- Can be edited manually (advanced users)
- Deleted when expert is deleted via UI

**See also**: [Expert Configuration Guide](expert-configs.md)

---

### 2. User Preferences (`.streamlit/app_defaults.toml`)

**Purpose**: Store default LLM settings, language preference and display settings

**Location**: `.streamlit/app_defaults.toml`

**Format**: TOML

**Example**:
```toml
[llm]
provider = "deepseek"
model = "deepseek-flash"
thinking_level = "high"

[language]
code = "en"

[display]
git_branch = true
```

**Settings**:
- **provider**: Default LLM provider (deepseek, openai, zai, kimi)
- **model**: Default model for the provider
- **thinking_level**: Default reasoning level (model-dependent: none, low, medium, high, xhigh, max; unsupported levels fall back to the model's default)
- **language.code**: UI language code
- **display.git_branch**: Show the Git branch in the sidebar footer

**Management**:
- Created on first run (auto-detects language)
- Updated via Settings page
- Can be edited manually

**See also**: [App Defaults Guide](app-defaults.md)

---

### 3. Theme Settings (`.streamlit/config.toml`)

**Purpose**: UI appearance customization (plus Streamlit client, browser and logger settings)

**Location**: `.streamlit/config.toml`

**Format**: TOML

**Example**:
```toml
[theme]
base = ".streamlit/themes/dark_gray.toml"
```

**Settings**:
- **theme.base**: Path to a theme file in `.streamlit/themes/` (e.g. `dark_gray.toml`, `ocean_blue.toml`, `custom.toml`). The colors (`primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, fonts, ...) live in that theme file, not in `config.toml`

**Management**:
- Created on app start from `config.toml.example` if missing
- Theme selected and saved via Settings → General ("Save & Apply Theme"); custom colors are written to `.streamlit/themes/custom.toml`
- Can be edited manually

---

### 4. API Keys (`.streamlit/secrets.toml`)

**Purpose**: Store API keys for LLM providers

**Location**: `.streamlit/secrets.toml`

**Format**: TOML

**Example**:
```toml
DEEPSEEK_API_KEY = "sk-..."
OPENAI_API_KEY = "sk-..."
ZAI_API_KEY = "..."
MOONSHOT_API_KEY = "sk-..."
```

**Providers**:
- **DEEPSEEK_API_KEY**: For DeepSeek API
- **OPENAI_API_KEY**: For OpenAI API (also voice input via `gpt-transcribe` for OpenAI experts)
- **ZAI_API_KEY**: For Z.AI API (also voice input via `glm-asr-2512` for all other experts)
- **MOONSHOT_API_KEY**: For KIMI API

**Security**:
- **File permissions**: Automatically set to 600 (owner read/write only)
- **Git status**: Ignored (not tracked in version control)
- **Validation**: Provider-specific key format check before saving

**Management**:
- Created via Settings page (recommended)
- Can be created manually from example file
- Updated via Settings page

**See also**: [API Keys Guide](api-keys.md)

## File Locations

### Project Root Structure

```
expertgpts/
├── .streamlit/
│   ├── secrets.toml              # API keys (gitignored)
│   ├── secrets.toml.example      # Template for secrets
│   ├── config.toml               # Theme settings (gitignored)
│   ├── config.toml.example       # Template for theme
│   ├── app_defaults.toml         # User preferences (gitignored)
│   └── app_defaults.toml.example # Template for defaults
│   └── themes/                   # Theme files referenced by config.toml
├── configs/
│   ├── 1001_helpful_assistant.yaml  # Expert configurations
│   ├── 1002_email_assistant.yaml
│   └── ...
├── pages/
│   ├── 1000_Home.py
│   ├── 1001_helpful_assistant.py
│   └── ...
├── chat_history/
│   ├── 1001_helpful_assistant.json  # Conversation history
│   └── ...
└── chat_attachments/
    ├── 1001_helpful_assistant/      # Images attached in the chat
    └── ...
```

### Which Files Are Tracked in Git?

**Tracked** (committed to version control):
- `pages/1000_Home.py`, `pages/9998_Settings.py`, `pages/9999_Help.py`, `pages/_debug.py` - System pages
- `.streamlit/*.example` - Template files
- `.streamlit/themes/` - Theme files

**Not Tracked** (gitignored):
- `configs/` - Expert configurations (auto-generated)
- `pages/*.py` expert pages (auto-generated)
- `.streamlit/secrets.toml` - Contains sensitive API keys
- `.streamlit/config.toml` - Personal theme preferences
- `.streamlit/app_defaults.toml` - Personal user preferences
- `chat_history/*.json` - Personal conversation history
- `chat_attachments/` - Images attached in the chat (referenced from the chat history)

## Configuration Precedence

When multiple configuration sources exist, precedence is:

1. **Expert Config** (`configs/*.yaml`) (highest priority)
   - Expert-specific settings (provider, model, thinking level, temperature)
   - Loaded when expert page is accessed; chat toolbox changes are written here immediately

2. **User Defaults** (`.streamlit/app_defaults.toml`)
   - Default provider/model for new experts
   - User preferences

3. **Application Defaults** (lowest priority)
   - Hardcoded fallbacks in code (`lib/shared/constants.py`)

**Example**: Model setting precedence:
```
Expert config metadata.model (if set)
    ↓
Default model of the expert's provider (DEFAULT_MODELS in constants.py)
```

New experts start with the provider/model from `app_defaults.toml` (fallback: `deepseek` / `deepseek-flash`) and temperature `1.0`. The temperature sent to the API is then limited by the model: fixed values (`fixed_temperature`) override it and the provider's `max_temperature` caps it.

## Configuration Management

### Via UI (Recommended)

**Settings Page** (`:material/settings:`):
- **General Tab**: Theme, language
- **API Key Tab**: Manage API keys for all providers
- **Default LLM Tab**: Default provider, model and thinking level
- **Expert Management Tab**: Add, edit, delete experts
- **Danger Zone Tab**: Reset application
- **About Tab**: Version information

**Home Page** (`:material/home:`):
- Add experts ("Add Chat" in the sidebar)

**Expert Page** (chat toolbox below the chat input):
- Model, thinking level and temperature, saved to the expert config immediately

### Manual Configuration

**For Advanced Users**:

1. **Expert Configs**: Edit `configs/*.yaml` directly
2. **App Defaults**: Edit `.streamlit/app_defaults.toml`
3. **Theme**: Edit `.streamlit/config.toml`
4. **API Keys**: Edit `.streamlit/secrets.toml`

**Caution**:
- Manual editing requires understanding of file formats
- Invalid syntax can cause application errors
- Use UI when possible
- Backup files before manual editing

### Configuration Files

**Example Files** (Templates):
- `.streamlit/secrets.toml.example`
- `.streamlit/config.toml.example`
- `.streamlit/app_defaults.toml.example`

These provide reference for manual configuration.

## Configuration Lifecycle

### Creating Configuration

**Expert Configs**:
1. User creates expert via UI ("Add Chat" on Home page or Settings → Expert Management)
2. `PageGenerator` creates expert ID
3. `ConfigManager` saves YAML config
4. Expert page generated from template

**User Defaults**:
1. First run: Language auto-detected
2. Saved to `app_defaults.toml`
3. Default provider/model/thinking level saved via Settings → Default LLM ("Save Defaults")

**Theme Settings**:
1. User customizes theme (Settings page)
2. `config_toml_manager.save_theme_settings()` saves the theme path to `config.toml`
3. Applied after the automatic reload

**API Keys**:
1. User enters key via Settings page
2. `secrets_manager.save_provider_api_key()` saves to `secrets.toml`
3. File permissions set to 600

### Updating Configuration

**Via UI**:
- Changes saved immediately
- Applied to next action/expert load

**Manual Editing**:
- May require app restart
- Or cache invalidation

### Deleting Configuration

**Expert Configs**:
- Deleted via UI (Settings → Expert Management)
- Removes: YAML config, expert page (the chat history file in `chat_history/` is kept on disk)
- Irreversible

**Other Configs**:
- Delete file manually
- App falls back to defaults
- Re-create via UI or manual editing

## Configuration Validation

### Expert Configs

**Validated Fields**:
- `expert_id`: Must be unique, alphanumeric with underscores
- `expert_name`: Required, non-empty string
- `description`: Required, non-empty string
- `temperature`: Number between 0.0 and 2.0 (Z.AI: 0.0 to 1.0; fixed for OpenAI and KIMI models)
- `system_prompt`: String (can be multi-line with `|`)

**Validation Errors**:
- Shown in UI when creating/editing experts
- Invalid configs rejected
- Error messages guide corrections

### API Keys

**Validation**:
- Provider-specific format (regex) check; minimum 20 characters for unknown providers
- Checked via UI before saving
- No API call made (validation is format only)

**Note**: API keys are not verified against provider APIs during configuration.

## Configuration Backup and Restore

### Backup

**Expert Configs**:
```bash
cp -r configs/ configs.backup/
```

**All Settings**:
```bash
mkdir backup
cp .streamlit/*.toml backup/
cp -r configs/ backup/
cp -r chat_history/ backup/
cp -r chat_attachments/ backup/
```

### Restore

**Expert Configs**:
```bash
cp -r configs.backup/* configs/
```

**All Settings**:
```bash
cp backup/*.toml .streamlit/
cp -r backup/configs/* configs/
cp -r backup/chat_history/* chat_history/
cp -r backup/chat_attachments/ chat_attachments/
```

### Export/Import

**Export Expert Configs**:
```bash
tar czf expert-configs.tar.gz configs/
```

**Import Expert Configs**:
```bash
tar xzf expert-configs.tar.gz
```

**Note**: An expert only appears if its page (`pages/{expert_id}.py`) exists. Expert pages are gitignored, so copy them along with the configs (e.g. add the matching `pages/{expert_id}.py` files to the archive), then bring them in line with your current template:
```bash
uv run python scripts/regenerate_pages.py
```

Do not run `reset_application.py` after an import: it deletes all configs, including the imported ones.

## Configuration Security

### File Permissions

**Secured Files** (600 permissions):
- `.streamlit/secrets.toml` - API keys
- `.streamlit/config.toml` - Theme settings
- `.streamlit/app_defaults.toml` - User preferences
- `configs/*.yaml`, `chat_history/*.json` - Expert configs and chat history

**Verification**:
```bash
ls -la .streamlit/
# Should show: -rw------- for .toml files
```

**Permissions Set Automatically**:
- Created via UI: 600 permissions applied
- Manual creation: Must set manually
  ```bash
  chmod 600 .streamlit/secrets.toml
  ```

### Sensitive Data

**API Keys**:
- Never stored in expert configs
- Never logged or printed
- Read directly from `.streamlit/secrets.toml` by `lib/config/secrets_manager.py` (no environment variable fallback)
- Gitignored (not tracked in version control)

**Chat History**:
- Stored locally, not transmitted except to LLM API
- Gitignored (`chat_history/`, `chat_attachments/`)
- No sensitive metadata beyond messages

## Configuration Best Practices

### 1. Use UI for Configuration

**Recommended**: Manage settings via Settings page

**Benefits**:
- Automatic validation
- Immediate feedback
- Proper file permissions
- No syntax errors

### 2. Backup Before Manual Changes

**Workflow**:
1. Backup configuration files
2. Make manual changes
3. Test application
4. Restore if issues occur

### 3. Back Up Expert Configs

`configs/` and the expert pages are gitignored. To version your experts, keep them in a separate (private) repository or use the backup/export steps above (Settings → Danger Zone also offers a ZIP download of the configs).

**Why**:
- Tracks expert evolution
- Enables collaboration
- Provides backup
- Documents changes

**Don't Commit**:
- `.streamlit/secrets.toml` (API keys)
- `.streamlit/config.toml` (personal theme)
- `.streamlit/app_defaults.toml` (personal preferences)
- `chat_history/` (personal conversations)
- `chat_attachments/` (images attached in the chat)

### 4. Document Custom Configs

**For Custom Experts**:
- Add comments to YAML configs
- Document custom system prompts
- Note temperature rationale

**Example**:
```yaml
expert_id: "1005_sql_expert"
expert_name: "SQL Expert"
description: "Expert in SQL database design and query optimization"
# Temperature 0.3 for focused, accurate query recommendations
temperature: 0.3
system_prompt: |
  Custom prompt with specific guidelines...
# Created for: Production database optimization team
created_at: "2025-01-17T12:00:00.000000"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

Note: comments are lost when the app rewrites the file (e.g. after a change in the chat toolbox or the edit dialog).

## Troubleshooting

### Configuration Not Loading

**Problem**: Changes not taking effect

**Solutions**:
1. Restart the application
2. Check file syntax (YAML/TOML)
3. Verify file permissions
4. Clear browser cache

### Invalid Configuration

**Problem**: Application errors related to config

**Solutions**:
1. Check syntax (YAML indentation, TOML format)
2. Validate against example files
3. Restore from backup
4. Re-create via UI

### Expert Not Using Settings

**Problem**: Expert not using expected defaults

**Explanation**: Defaults only apply to new experts

**Solutions**:
1. Set defaults before creating experts
2. Or manually edit existing experts
3. Or edit expert config directly

## Next Steps

- **[Expert Configuration Guide](expert-configs.md)** - Expert YAML configs in detail
- **[API Keys Guide](api-keys.md)** - API key management
- **[App Defaults Guide](app-defaults.md)** - User preferences
- **[User Guide - Customization](../user-guide/customization.md)** - Settings page usage

---

**Back to**: [Documentation Home](../README.md)
