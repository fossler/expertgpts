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
│  Purpose: Default provider, model, language                 │
│  Managed: Via Settings page                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. THEME SETTINGS                                          │
│  Location: .streamlit/config.toml                           │
│  Purpose: UI appearance (colors, fonts)                     │
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
  version: "1.0"
  model: "deepseek-chat"
```

**Naming Convention**: `{expert_id}.yaml`

**Management**:
- Created automatically when adding experts via UI
- Can be edited manually (advanced users)
- Deleted when expert is deleted via UI

**See also**: [Expert Configuration Guide](expert-configs.md)

---

### 2. User Preferences (`.streamlit/app_defaults.toml`)

**Purpose**: Store default LLM settings and language preference

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

**Settings**:
- **provider**: Default LLM provider (deepseek, openai, zai)
- **model**: Default model for the provider
- **temperature**: Default temperature for new experts
- **thinking_level**: Default reasoning level (none, low, medium, high)
- **language.code**: UI language code

**Management**:
- Created on first run (auto-detects language)
- Updated via Settings page
- Can be edited manually

**See also**: [App Defaults Guide](app-defaults.md)

---

### 3. Theme Settings (`.streamlit/config.toml`)

**Purpose**: UI appearance customization

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

**Settings**:
- **primaryColor**: Buttons and interactive elements
- **backgroundColor**: Main content area
- **secondaryBackgroundColor**: Sidebar and secondary areas
- **textColor**: Main text color
- **font**: Font family (sans serif, serif, monospace)

**Management**:
- Created when theme is first customized
- Updated via Settings page
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
```

**Providers**:
- **DEEPSEEK_API_KEY**: For DeepSeek API
- **OPENAI_API_KEY**: For OpenAI API
- **ZAI_API_KEY**: For Z.AI API

**Security**:
- **File permissions**: Automatically set to 600 (owner read/write only)
- **Git status**: Ignored (not tracked in version control)
- **Validation**: Minimum 20 characters required

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
├── configs/
│   ├── 1001_python_expert.yaml   # Expert configurations
│   ├── 1002_data_scientist.yaml
│   └── ...
├── pages/
│   ├── 1000_Home.py
│   ├── 1001_python_expert.py
│   └── ...
└── chat_history/
    ├── 1001_python_expert.json   # Conversation history
    └── ...
```

### Which Files Are Tracked in Git?

**Tracked** (committed to version control):
- `configs/*.yaml` - Expert configurations
- `pages/*.py` - Expert pages
- `.streamlit/*.example` - Template files

**Not Tracked** (gitignored):
- `.streamlit/secrets.toml` - Contains sensitive API keys
- `.streamlit/config.toml` - Personal theme preferences
- `.streamlit/app_defaults.toml` - Personal user preferences
- `chat_history/*.json` - Personal conversation history

## Configuration Precedence

When multiple configuration sources exist, precedence is:

1. **Session State** (highest priority)
   - Current user session settings
   - Per-expert overrides

2. **Expert Config** (`configs/*.yaml`)
   - Expert-specific settings
   - Loaded when expert page is accessed

3. **User Defaults** (`.streamlit/app_defaults.toml`)
   - Default settings for new experts
   - User preferences

4. **Application Defaults** (lowest priority)
   - Hardcoded fallbacks in code

**Example**: Temperature setting precedence:
```
Session state override (if user changed in current session)
    ↓
Expert config temperature (if set)
    ↓
App defaults temperature (global default)
    ↓
Application default (0.7)
```

## Configuration Management

### Via UI (Recommended)

**Settings Page** (`:material/settings:`):
- **General Tab**: Theme, language, provider/model defaults
- **API Keys Tab**: Manage API keys for all providers
- **About Tab**: Version information

**Home Page** (`:material/home:`):
- Add, edit, delete experts
- Expert configuration managed via forms

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
1. User creates expert via UI (Home page)
2. `PageGenerator` creates expert ID
3. `ConfigManager` saves YAML config
4. Expert page generated from template

**User Defaults**:
1. First run: Language auto-detected
2. Saved to `app_defaults.toml`
3. Default provider/model saved when changed

**Theme Settings**:
1. User customizes theme (Settings page)
2. `ConfigTomlManager` saves to `config.toml`
3. Applied immediately

**API Keys**:
1. User enters key via Settings page
2. `SecretsManager` saves to `secrets.toml`
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
- Deleted via UI (Home page)
- Removes: YAML config, expert page, chat history
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
- `temperature`: Number between 0.0 and 2.0
- `system_prompt`: String (can be multi-line with `|`)

**Validation Errors**:
- Shown in UI when creating/editing experts
- Invalid configs rejected
- Error messages guide corrections

### API Keys

**Validation**:
- Minimum 20 characters
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

**Note**: Imported configs require expert pages to be regenerated:
```bash
python3 scripts/reset_application.py
```

## Configuration Security

### File Permissions

**Secured Files** (600 permissions):
- `.streamlit/secrets.toml` - API keys
- `.streamlit/config.toml` - Theme settings
- `.streamlit/app_defaults.toml` - User preferences

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
- Only accessed via Streamlit secrets API
- Gitignored (not tracked in version control)

**Chat History**:
- Stored locally, not transmitted except to LLM API
- Gitignored
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

### 3. Version Control Expert Configs

**Recommended**: Commit expert configs to git

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
  version: "1.0"
  model: "deepseek-chat"
```

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
