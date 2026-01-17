# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Guidelines

### Commit Policy
**IMPORTANT: Do NOT commit changes automatically.**

When making changes to the codebase:
1. Make the requested changes
2. Show what was modified
3. Wait for user review
4. Only commit when user explicitly requests it with "commit" or similar command

This allows the user to review changes before they're committed to the repository.

### DRY Principle (Don't Repeat Yourself)

**CRITICAL:** Always follow the DRY principle when making changes to this codebase.

#### Guidelines:

1. **Before writing any code:**
   - Search for existing implementations that do the same thing

2. **When you find duplicated code:**
   - Extract it to a shared function in the appropriate `utils/` module
   - Update ALL locations to use the shared function
   - Update templates AND generated pages
   - Test to ensure no regressions

3. **Common patterns that should be shared:**
   - Form fields (temperature, text inputs, etc.)
   - Validation logic (expert names, descriptions, etc.)
   - Dialog rendering (add, edit, delete)
   - Documentation content (constants)
   - **i18n translations**: Import `i18n` at module level, never inline in functions
   - **Expert name translations**: Use `sanitize_name()` to generate keys dynamically

4. **Checklist before committing:**
   - [ ] Did I search for existing implementations?
   - [ ] Is this code duplicated anywhere else?
   - [ ] Did I update all templates?
   - [ ] Did I update all generated pages?

### No Backward Compatibility

**IMPORTANT: Do NOT maintain backward compatibility code.**

When refactoring or changing data structures:
- Remove old code paths immediately
- Do NOT add "legacy" support or migration logic
- Assume all configs and data will be regenerated from scratch
- The user can run `scripts/reset_application.py` to recreate everything

**Rationale:**
- This is a personal project with a small number of experts
- Configs are easy to regenerate
- Backward compatibility adds complexity and technical debt
- Clean code is more valuable than supporting old data formats


## Project Overview

ExpertGPTs is a multi-expert AI chat application built with Streamlit, powered by the DeepSeek API. It uses a **template-based architecture** where each domain-specific expert agent is generated from a single template, with behavior controlled by YAML configuration files.

## Key Architecture Concepts

### Template-Based Page Generation
- **All expert pages** are generated from `templates/template.py`
- **Home and Settings pages** are permanent files in `pages/` (not generated)
- **PageGenerator** creates numbered Python files (e.g., `1_Python_Expert.py`) from the template
- Placeholders `{{EXPERT_ID}}` and `{{EXPERT_NAME}}` are replaced during generation
- **Never manually edit expert pages** - changes will be lost when regenerated
- To modify all experts, edit `templates/template.py` instead

### Expert Configuration System
Each expert has a corresponding YAML config file in `configs/`:
- **Format**: `{timestamp}_{safe_name}.yaml`
- **Contains**: expert_id, expert_name, description, temperature, system_prompt, metadata
- **System prompts** are auto-generated from description if not provided
- Config is loaded at runtime via `ConfigManager.load_config()`

### Session State Architecture
Critical pattern for expert isolation:
- **Chat history per expert**: `st.session_state[f"messages_{EXPERT_ID}"]` - prevents cross-contamination
- **Shared API key**: `st.session_state.deepseek_api_key` - available across all experts, loaded from `st.secrets["DEEPSEEK_API_KEY"]`
- **Navigation state**: `st.session_state.pending_expert_page` - for auto-navigation after creation

### Streamlit Navigation Architecture
- **Modern approach**: Uses `st.navigation()` API in `app.py` for page management
- **Home page**: `pages/1000_Home.py` (permanent file, committed to git)
- **Expert pages**: `pages/1001_*.py`, `pages/1002_*.py`, etc. (generated from `templates/template.py`)
- **Settings page**: `pages/9999_Settings.py` (permanent file, committed to git)
- **Dynamic loading**: Expert pages discovered automatically via `PageGenerator.list_pages()`
- **Page creation**: New pages require `st.rerun()` to be discovered by the navigation system
- **Navigation icons**: Uses Material Design icons (e.g., `:material/home:`, `:material/psychology:`)

## Essential Commands

### Development Setup
```bash
# Always use .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt  # Development (includes watchdog, pytest, black)
pip install -r requirements.txt        # Production only

# Set up API key (optional - can also do via UI)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Then edit .streamlit/secrets.toml and add your DEEPSEEK_API_KEY

# Run the app (first run will automatically create example experts)
streamlit run app.py
```

### Application Reset
```bash
# Reset application to factory default state
# WARNING: This deletes all configs and expert pages, then recreates example experts
# IMPORTANT: Home and Settings pages are preserved (they're permanent files)
# IMPORTANT: Always use echo "yes" | to auto-confirm (required for non-interactive environments)
echo "yes" | python3 scripts/reset_application.py

# Or make executable and run directly
chmod +x scripts/reset_application.py
echo "yes" | ./scripts/reset_application.py
```

**Use scripts/reset_application.py when:**
- After modifying `templates/template.py` and need to regenerate all expert pages
- Configs and pages become out of sync or corrupted
- Starting fresh for development/testing


### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agent_generation.py

# Run specific test
pytest tests/test_agent_generation.py::TestAgentGeneration::test_create_config

# Run with coverage
pytest --cov=utils --cov-report=html

# Quick test run
./scripts/run_tests.sh
```

### Code Quality
```bash
# Format code (if black is installed)
black .

# Check import issues
python -m pytest --collect-only  # Verifies imports without running tests
```

## Important Workflows

### Creating a New Expert Agent
When users create an expert through the UI:
1. Form submission → `ConfigManager.create_config()` generates YAML config with unique ID
2. `PageGenerator.generate_page()` creates numbered page file from template
3. `st.rerun()` triggers Streamlit to discover the new page
4. `st.switch_page()` automatically navigates to the new expert

**Manual expert creation** (for testing):
```python
from utils.config_manager import ConfigManager
from utils.page_generator import PageGenerator

config_manager = ConfigManager()
page_generator = PageGenerator()

expert_id = config_manager.create_config(
    expert_name="Test Expert",
    description="An expert in testing...",
    temperature=0.7,
)

page_path = page_generator.generate_page(
    expert_id=expert_id,
    expert_name="Test Expert",
)
```

### Understanding Chat Flow
1. User input → stored in `st.session_state[f"messages_{EXPERT_ID}"]`
2. LLMClient initialized with provider-specific API key (from client pool)
3. `client.chat_stream()` sends messages with system prompt to LLM provider API
4. Streaming response accumulated character by character
5. Complete response added to session state for context

### Modifying Expert Behavior
- **Temperature**: Edit YAML config file or use UI when creating
- **System Prompt**: Provide custom prompt via "Advanced: Custom System Prompt" field
- **All Experts**: Edit `templates/template.py` (changes require regenerating pages)
  - After modifying template, run `python3 scripts/reset_application.py` to regenerate all experts
- **Single Expert**: Edit specific page file directly (but loses template consistency)

## File Structure Notes

- **`templates/template.py`**: Master template for expert pages - edit this to change all expert pages
- **`pages/`**: Contains both permanent and generated pages
  - **`pages/1000_Home.py`**: Home page (permanent, committed to git)
  - **`pages/1001_*.py`**: Expert pages (auto-generated from template, gitignored)
  - **`pages/9999_Settings.py`**: Settings page (permanent, committed to git)
- **`configs/`**: YAML configs - **gitignored** (regenerated by setup scripts)
- **`icons/`**: Application icons (OpenAI logos, etc.)
- **`utils/`**: Shared business logic - modular, testable components
  - **`utils/secrets_manager.py`**: Manages `.streamlit/secrets.toml` for API key storage
  - **`utils/config_toml_manager.py`**: Manages `.streamlit/config.toml` for theme settings
  - **`utils/app_defaults_manager.py`**: Manages `.streamlit/app_defaults.toml` for user preferences (LLM defaults, language)
  - **`utils/session_state.py`**: Manages shared session state initialization
  - **`utils/dialogs.py`**: Shared dialog components (DRY compliance)
  - **`utils/constants.py`**: Shared constants and documentation (DRY compliance)
- **`tests/`**: Test suite using pytest with temporary directories for isolation
- **`scripts/setup.py`**: Sets up the application (creates 7 default example experts on first run)
- **`scripts/reset_application.py`**: Resets app to factory state (deletes expert pages and configs, then runs setup.py)
- **`.streamlit/`**: Streamlit configuration directory
  - **`secrets.toml`**: API keys and secrets - **gitignored** (auto-created by app)
  - **`secrets.toml.example`**: Template file for manual setup
  - **`config.toml`**: Theme and appearance settings - **gitignored** (managed through Settings page)
  - **`config.toml.example`**: Template file for theme settings
  - **`app_defaults.toml`**: User preferences (LLM defaults, language) - **gitignored** (auto-created by app)
  - **`app_defaults.toml.example`**: Template file for app defaults

**Important**:
- `configs/` is fully in `.gitignore` since configs are auto-generated
- `pages/` contains both permanent files (committed to git) and auto-generated files (gitignored):
  - Permanent: `pages/1000_Home.py` and `pages/9999_Settings.py` (committed to git)
  - Auto-generated: Expert pages like `pages/1001_*.py`, `pages/1002_*.py`, etc. (gitignored)
- To recreate auto-generated content, run `scripts/setup.py` or `scripts/reset_application.py`
- `.streamlit/app_defaults.toml` contains user preferences (not auto-generated, but gitignored for privacy)

## Key Implementation Details

### Session State Isolation Pattern
```python
# WRONG - shared across all experts
if "messages" not in st.session_state:
    st.session_state.messages = []

# RIGHT - isolated per expert
messages_key = f"messages_{EXPERT_ID}"
if messages_key not in st.session_state:
    st.session_state[messages_key] = []
```

### Page Discovery Timing
After creating a new page file, Streamlit won't see it until rerun:
```python
# Create page
page_path = page_generator.generate_page(...)

# Store for navigation after rerun
st.session_state.pending_expert_page = page_path

# Trigger rerun (Streamlit discovers new page)
st.rerun()

# Next run: check for pending navigation and switch
if st.session_state.get("pending_expert_page"):
    st.switch_page(st.session_state.pending_expert_page)
```

### API Key Management with Streamlit Secrets
**ExpertGPTs uses Streamlit's recommended secrets management system:**

- **Storage**: API keys stored in `.streamlit/secrets.toml` (gitignored)
- **Access**: Keys accessed via `st.secrets["DEEPSEEK_API_KEY"]`
- **UI Management**: Users can set/clear API keys through the Settings page
- **Automatic Saving**: When entered via UI, keys are automatically saved to `secrets.toml`
- **Session State**: Keys also stored in `st.session_state.deepseek_api_key` for immediate use

**Setting up API keys:**
1. **Via UI** (Recommended): Go to Settings → API Key tab → Enter key → Click "Save API Key"
2. **Manually**: Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your key

**Key utilities in `utils/secrets_manager.py`:**
- `save_provider_api_key(provider, api_key)` - Saves provider-specific API key to secrets.toml with secure 600 permissions
- `get_provider_api_key(provider)` - Reads provider API key directly from file (for status display)
- `has_provider_api_key(provider)` - Checks if provider API key exists in file
- `get_all_provider_api_keys()` - Returns dictionary of all provider API keys
- `ensure_secrets_file_exists()` - Creates .streamlit directory and file if needed
- `set_secure_permissions(file_path)` - Sets 600 permissions (owner read/write only)

**IMPORTANT:**
- Never commit `.streamlit/secrets.toml` to git (it's in .gitignore)
- API keys are accessed via `st.secrets` using provider-specific environment variable names (e.g., `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `ZAI_API_KEY`)

### Theme Customization

ExpertGPTs supports full theme customization through the Settings page:

**Accessing Theme Settings:**
1. Go to Settings → General tab
2. Use color pickers to customize:
   - **Buttons and interactive Elements**: Color for buttons and interactive elements
   - **Background Color**: Main background
   - **Secondary Background**: Sidebar and secondary areas
   - **Text Color**: Main text throughout the app

**Preset Themes:**
- Light themes: Red, Blue, Green, Purple
- Dark themes: Dark Blue, Dark Gray
- Click any preset to instantly apply

**Key utilities in `utils/config_toml_manager.py`:**
- `get_theme_settings()` - Get current theme colors
- `save_theme_settings(...)` - Save new theme colors
- `reset_to_default_theme()` - Reset to default colors
- Settings automatically saved to `.streamlit/config.toml` with 600 permissions

### Internationalization (i18n)

ExpertGPTs supports 13 languages with a comprehensive i18n system:

**Architecture:**
- **Storage Layer**: Expert content (YAML configs) stored in English only
- **Translation Layer**: UI translations in JSON files (`locales/ui/{lang}.json`)
- **Runtime Layer**: Language prefix dynamically injected for AI responses

**Key Features:**
- ✅ Auto-detection of system language
- ✅ Instant language switching (no expert regeneration needed)
- ✅ All UI elements translated (buttons, labels, errors, success messages)
- ✅ Default expert names translated to all 13 languages
- ✅ Professional logging instead of print statements
- ✅ Cached language access for performance (~50% reduction in lookups)

**Important i18n utilities:**
- `utils/i18n.py`: `I18nManager` class with translation and language detection
- `utils/helpers.py`: `translate_expert_name()` - Dynamic expert name translation
- `utils/app_defaults_manager.py`: `get_language_preference()` / `save_language_preference()`
- `scripts/update_translations.py`: Sync all locale files with `en.json`

**Best Practices for i18n:**
- **Always** import `i18n` at module level (never inline in functions)
- **Always** use `i18n.t('key')` for UI strings, never hardcode
- **Always** add new translation keys to `en.json` first (source of truth)
- **Always** run `update_translations.py` after adding new keys
- **Never** add expert content (system prompts) to locale files
- **Never** create duplicate expert name mappings - use `sanitize_name()` dynamically

**Example Usage:**
```python
# ✅ GOOD - Module level import
from utils.i18n import i18n

# Simple translation
text = i18n.t('home.title')

# With parameters
text = i18n.t('errors.error', error=str(e))

# Access current language (cached)
lang = i18n.current_language
```

**For detailed i18n documentation**, see `docs/I18N_GUIDE.md`

### Application Defaults

ExpertGPTs persists user preferences in `.streamlit/app_defaults.toml`:

**What's Stored:**
- **LLM Defaults**: Default provider, model, and thinking level
- **Language**: Interface language preference
- **Future**: UI preferences, feature flags, etc.

**File Structure:**
```toml
[llm]
provider = "deepseek"
model = "deepseek-chat"
thinking_level = "none"

[language]
code = "en"
```

**Key utilities:**
- `utils/app_defaults_manager.py`: All app defaults persistence
  - `get_llm_defaults()` / `save_llm_defaults()`
  - `get_language_preference()` / `save_language_preference()`
  - `has_app_defaults()` / `reset_app_defaults()`

**How It Works:**
1. **On startup**: `initialize_shared_session_state()` loads defaults from TOML
2. **When changed**: Settings page saves to TOML on "Save" button click
3. **Persistence**: Settings survive app restarts and browser closes

**Security:**
- File permissions: 600 (owner read/write only)
- Location: `.streamlit/` (gitignored)
- No secrets: Only preferences, not API keys

**Example Usage:**
```python
from utils.app_defaults_manager import (
    get_llm_defaults,
    save_llm_defaults,
    get_language_preference,
    save_language_preference
)

# Load defaults
llm = get_llm_defaults()
lang = get_language_preference()

# Save defaults
save_llm_defaults("openai", "gpt-5", "medium")
save_language_preference("de")
```

## Common Pitfalls

1. **Editing expert pages directly** - Changes lost on regeneration
2. **Not using .venv** - Dependencies or versions may be incorrect
3. **Forgetting `st.rerun()`** after page creation - New page won't be discoverable
4. **Shared session state keys** - Chat history contaminates between experts
5. **Hardcoding paths** - Use `Path(__file__).parent` for relative paths
6. **Not regenerating pages** after template changes - Old pages use outdated code
   - Solution: Run `python3 scripts/reset_application.py` after modifying template
7. **Importing i18n inline** - Violates DRY and hurts performance
   - Solution: Always import `i18n` at module level
8. **Hardcoding UI strings** - Breaks i18n and creates maintenance burden
   - Solution: Always use `i18n.t('key')` for user-facing text
9. **Creating duplicate expert name mappings** - Violates DRY principle
   - Solution: Use `sanitize_name()` to generate translation keys dynamically

## Testing Approach

Tests use **temporary directories** via `tmp_path` fixture to avoid polluting the project:
- Temporary configs directory
- Temporary pages directory
- Copy of actual template
- Automatic cleanup after tests

Always use **fictitious test data**, never real user information.

---

## Recent Architectural Changes

### Migration to st.navigation() API

The application has been updated to use Streamlit's modern `st.navigation()` API (available in Streamlit 1.28+). This is a significant architectural improvement over the older automatic page discovery pattern.

**Key changes:**
- **Centralized navigation**: All page routing defined in `app.py` using `st.navigation()`
- **Dynamic page loading**: Expert pages discovered via `PageGenerator.list_pages()`
- **Material Design icons**: Navigation uses icon syntax (e.g., `:material/home:`, `:material/psychology:`)
- **Improved UX**: Better navigation control and state management

**Benefits:**
- More robust page discovery and navigation
- Better control over page ordering and icons
- Cleaner separation between navigation logic and page content
- Easier to add new navigation features

**Impact on development:**
- New pages must follow numbering scheme: Home (1000), Experts (1001+), Settings (9999)
- Icons must use Material Design syntax
- All page templates should maintain consistency with navigation structure
