# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ExpertGPTs is a multi-expert AI chat application built with Streamlit that provides access to domain-specific AI experts (Python, Data Science, Writing, etc.) with support for multiple LLM providers (DeepSeek, OpenAI, Z.AI), full internationalization (13 languages), template-based page generation, and persistent chat history.

## Working Guidelines

### DRY Principle (Don't Repeat Yourself)

**CRITICAL:** Always follow the DRY principle when making changes to this codebase.

#### Guidelines:

1. **Before writing any code:**
   - Search for existing implementations that do the same thing

2. **When you find duplicated code:**
   - Extract it to a shared function in the appropriate `lib/` subdirectory
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


## Reference Documentation

Read these documents when working on specific areas:

| Document | When to Read |
|----------|--------------|
| `docs/architecture/overview.md` | Understanding overall system architecture |
| `docs/architecture/template-system.md` | Modifying expert page templates |
| `docs/architecture/multi-provider-llm.md` | Adding LLM providers, thinking parameters |
| `docs/architecture/background-streaming.md` | Streaming implementation, battery optimization |
| `docs/architecture/state-management.md` | Session state, persistent storage |
| `docs/internationalization/I18N_GUIDE.md` | Adding translations, language handling |
| `docs/configuration/overview.md` | Configuration files structure |
| `docs/configuration/api-keys.md` | API key management, secrets |
| `docs/configuration/expert-configs.md` | Expert YAML configuration format |
| `docs/development/adding-features.md` | Step-by-step feature development |
| `docs/development/testing.md` | Writing and running tests |
| `docs/reference/troubleshooting.md` | Debugging common issues |


## Development Commands

### Setup & Installation
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt  # Development (includes watchdog, pytest)
pip install -r requirements.txt       # Production only

# First-time setup (creates 7 example experts)
python3 scripts/setup.py
```

### Running the Application
```bash
# Start the Streamlit app
streamlit run app.py

# With enhanced file watching (faster reload during development)
streamlit run app.py --server.fileWatcherType=watchdog
```

### Testing
```bash
# Run all tests (recommended)
./scripts/run_tests.sh

# Direct pytest commands
source .venv/bin/activate
python -m pytest -v                           # All tests
python -m pytest -v -m "unit"                # Unit tests only
python -m pytest -v -m "integration"         # Integration tests only
python -m pytest -v -m "not slow"            # Exclude slow tests
```

### Code Quality
```bash
# Format code with Black
black .

# Check formatting without making changes
black --check .
```

### Administrative Scripts
```bash
# Reset application - regenerates all expert pages from template
echo "yes" | python3 scripts/reset_application.py

# Update translations - syncs English source with all locale files
python3 scripts/update_translations.py
```

## Architecture Patterns

### 1. Template-Based Expert System

The application uses a **template-driven architecture** where expert pages are generated from a single template:

- **Permanent pages** (committed to git): `pages/1000_Home.py` and `pages/9998_Settings.py`
- **Generated expert pages** (auto-generated): `pages/1001_*.py` and higher
- **Template source**: `templates/template.py` with `{{EXPERT_ID}}` and `{{EXPERT_NAME}}` placeholders
- **Configuration files**: Each expert has a YAML config in `configs/{expert_id}.yaml`
- **Page numbering scheme**: Home (1000) → Experts (1001+) → Settings (9999)

**Key insight**: When modifying expert page UI/UX, edit the template and regenerate all pages. When modifying Home/Settings, edit the permanent files directly.

### 2. Multi-Provider LLM Abstraction

A unified client interface supports multiple LLM providers through OpenAI-compatible APIs:

- **Client implementation**: `lib/llm/llm_client.py` - `LLMClient` class
- **Provider-specific thinking parameters**:
  - **OpenAI**: `reasoning_effort` (low/medium/high) - passed as direct parameter
  - **DeepSeek**: `thinking.type` (enabled/disabled) - determined by model selection (`deepseek-chat` vs `deepseek-reasoner`)
  - **Z.AI**: `thinking.type` (enabled/disabled) - set via extra_body parameter
- **Provider configuration**: Centralized in `lib/shared/constants.py` with O(1) lookup tables
- **Connection pooling**: `lib/llm/client_pool.py` caches client instances for performance

**Key insight**: All three providers use the OpenAI Python client with custom `base_url`. Provider differences are handled in `_prepare_thinking_param()` method.

### 3. State Management

Multi-layered state system with different lifetimes:

- **Shared session state** (initialized once per session):
  - API keys for all providers (`st.session_state["api_keys"]`)
  - Default LLM settings (provider, model, temperature)
  - Language preference
  - Navigation state

- **Per-expert session state** (separate for each expert):
  - Messages history: `st.session_state[f"messages_{expert_id}"]`
  - Provider selection: `st.session_state[f"provider_{expert_id}"]`
  - Model selection: `st.session_state[f"model_{expert_id}"]`
  - Temperature: `st.session_state[f"temperature_{expert_id}"]`
  - Thinking level: `st.session_state[f"thinking_{expert_id}"]`

- **Persistent storage** (survives app restarts):
  - Chat history: `chat_history/{expert_id}.json` (1MB file size limit)
  - Expert configurations: `configs/{expert_id}.yaml`
  - User preferences: `.streamlit/app_defaults.toml`
  - Theme settings: `.streamlit/config.toml`

**Key insight**: Session state initialization happens in two phases - shared state first (via `initialize_shared_session_state()`), then per-expert state with chat history loading.

### 4. Background Streaming System

Battery-optimized file-based caching that allows LLM responses to complete in the background when users navigate away:

- **Implementation**: `lib/storage/streaming_cache.py` - `StreamingCache` class
- **Fixed filenames**: `{expert_id}_latest.txt` and `{expert_id}_latest.meta` per expert
- **Daemon threads**: Background threads write chunks to cache files with `fsync()` for crash resilience
- **Polling mechanism**: Foreground polls cache files every 100ms (battery-optimized: 2-3% CPU vs 5-10% for session state polling)
- **Smart cleanup**: Only deletes completed/error streams, preserves in-progress streams
- **Thread safety**: OS-level file locking prevents corruption

**Key features:**
- ✅ Real-time streaming with blinking cursor (`▌`)
- ✅ Background completion when navigating away
- ✅ Automatic resume when returning to page
- ✅ Survives app crashes and restarts
- ✅ Easy debugging (inspect `.txt` cache files)
- ✅ Follows DRY principle (mirrors `chat_history_manager.py` pattern)

**Key insight**: File I/O uses DMA (Direct Memory Access), allowing CPU to enter deep sleep states between reads. This provides significantly better battery life on notebooks compared to session state polling approaches.

**Usage in template:**
```python
# Start background streaming
cache = StreamingCache(EXPERT_ID)
cache.start_streaming_to_file(client, messages, temperature, model, system_prompt, thinking_level)

# Poll for updates
response = poll_stream_and_display(cache, EXPERT_ID, messages_key, message_placeholder)

# Resume incomplete streams on page load
check_and_display_cached_responses(config, messages_key)
```

### 5. Three-Layer Internationalization

Clean separation of concerns for 13-language support:

```
┌─────────────────────────────────────────────────────────┐
│  1. STORAGE LAYER (configs/*.yaml)                      │
│  Expert content in English - Single Source of Truth     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. TRANSLATION LAYER (locales/ui/*.json)               │
│  UI translations ONLY - Buttons, labels, messages       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. RUNTIME LAYER (template.py, i18n.py)                │
│  Language prefix injection: "Respond in German"         │
└─────────────────────────────────────────────────────────┘
```

**Implementation**: `i18n.get_language_prefix()` injects language instruction into system prompts at runtime, ensuring AI responds in user's selected language while expert content remains in English.

**Key insight**: Never translate expert content in YAML configs. Only UI elements go in locale files. Language selection auto-detects on first run and persists in `app_defaults.toml`.

## Critical Files Reference

### Core Application
- **`app.py`** - Main entry point using `st.navigation()`; handles first-run detection and dynamic page loading
- **`templates/template.py`** - Master template for all expert pages; edit here then regenerate to update all experts
- **`pages/1000_Home.py`** - Home page with expert list and "Add Chat" functionality (permanent file)
- **`pages/9998_Settings.py`** - Settings page for API keys, themes, language, provider defaults (permanent file)
- **`pages/9999_Help.py`** - Help page with documentation and links (permanent file)

### Core Library (`lib/`)
- **`config_manager.py`** - Expert YAML config operations (load, update, delete, list)
- **`page_generator.py`** - Creates new expert pages from template; generates unique expert IDs
- **`llm_client.py`** - Multi-provider LLM client; handles thinking parameter differences via `_prepare_thinking_param()`
- **`client_pool.py`** - Cached client connections; use `get_cached_client()` instead of direct instantiation
- **`secrets_manager.py`** - Secure API key management; reads/writes `.streamlit/secrets.toml` with 600 permissions
- **`app_defaults_manager.py`** - User preferences management (default provider, model, language)
- **`config_toml_manager.py`** - Theme configuration management for `.streamlit/config.toml`
- **`chat_history_manager.py`** - Persistent conversation storage; enforces 1MB file size limit
- **`session_state.py`** - Initializes shared session state (API keys, navigation, defaults) - **UPDATED**: Added `ensure_dialog_state()` helper
- **`streaming_cache.py`** - Background streaming with file-based caching; battery-optimized polling for LLM responses
- **`token_manager.py`** - Token counting and context usage tracking; calculates percentage of context used
- **`i18n.py`** - Internationalization engine; loads locale files and injects language prefixes
- **`constants.py`** - Provider/model configurations; defines `LLM_PROVIDERS` dict and O(1) lookup tables
- **`helpers.py`** - Utility functions including `translate_expert_name()` for default expert names
- **`file_ops.py`** - Shared file system operations - **UPDATED**: Added `ensure_streamlit_file()` helper
- **`format_ops.py`** - Shared file format operations (TOML, YAML, JSON read/write)

### Configuration Files
- **`.streamlit/secrets.toml`** - API keys (gitignored, auto-set to 600 permissions)
- **`.streamlit/config.toml`** - Theme settings (gitignored)
- **`.streamlit/app_defaults.toml`** - User preferences (gitignored)
- **`.streamlit/*.example`** - Template files for configuration (committed to git)
- **`configs/{expert_id}.yaml`** - Expert-specific configurations (name, description, system_prompt, temperature, metadata)

### Documentation
- **`README.md`** - Comprehensive user and developer documentation
- **`docs/`** - Full documentation organized by topic (see Reference Documentation section above)

## Important Development Workflows

### Modifying Expert Pages

**To update ALL expert pages** (UI, layout, functionality):
1. Edit `templates/template.py`
2. Run `echo "yes" | python3 scripts/reset_application.py`
3. All expert pages (1001+) are regenerated from the updated template

**To update Home or Settings pages only**:
- Edit `pages/1000_Home.py` or `pages/9998_Settings.py` directly (these are permanent files)
- No regeneration needed

**Key insight**: The template uses `{{EXPERT_ID}}` and `{{EXPERT_NAME}}` placeholders. The page generator replaces these when creating new expert pages.

### Adding a New LLM Provider

1. **Add provider configuration** in `lib/shared/constants.py`:
   - Add entry to `LLM_PROVIDERS` dict with name, base_url, default_model, models dict
   - Models must include: display_name, max_tokens, thinking_param

2. **Update thinking parameter handling** in `lib/llm/llm_client.py`:
   - Modify `_prepare_thinking_param()` method if provider uses custom thinking parameters
   - Return format: `(extra_body_dict, direct_params_dict)`

3. **Add API key UI** in `pages/9998_Settings.py`:
   - Add input field in API Keys tab for new provider

4. **Update secrets template**:
   - Add `{PROVIDER}_API_KEY = ""` to `.streamlit/secrets.toml.example`

5. **Update lookup tables** in `lib/shared/constants.py`:
   - Existing code automatically generates lookup tables from `LLM_PROVIDERS`

### Creating a New Expert

**Via UI** (recommended):
1. Go to Home page
2. Click "➕ Add Chat" in sidebar
3. Fill form: name, description, temperature, optional custom system prompt
4. Page automatically generated and navigated to

**Programmatically**:
```python
from utils.page_generator import PageGenerator

generator = PageGenerator()
expert_id = generator.generate_page(
    expert_name="My Expert",
    description="Expert in...",
    temperature=0.7,
    system_prompt="Custom prompt...",
    provider="deepseek",
    model="deepseek-chat"
)
```

### Internationalization

**Adding a new UI string translation**:
1. Add string to all locale files: `locales/ui/{language}.json`
2. Use in code: `i18n.t("key.path")`
3. Update `scripts/update_translations.py` if needed

**Key principle**:
- **Expert content** (name, description, system_prompt): Keep in English in YAML configs
- **UI elements** (buttons, labels, errors): Translate in locale files
- **AI responses**: Automatically in user's language via runtime prefix injection

### Debugging Common Issues

**Expert not appearing in navigation**:
- Check expert page file exists in `pages/` with correct numbering (1001+)
- Verify corresponding config exists in `configs/`
- Streamlit auto-discovers pages; may need momentary wait

**"Configuration not found" error**:
- Run `python3 scripts/setup.py` to create example experts
- Verify `configs/{expert_id}.yaml` exists

**API key errors**:
- Check `.streamlit/secrets.toml` exists and has valid key (min 20 characters)
- Verify permissions: `ls -la .streamlit/secrets.toml` should show `-rw-------`
- Set key via Settings page for automatic permission management

**Chat history not persisting**:
- Check `chat_history/` directory exists
- Verify file size under 1MB limit
- Check `save_chat_history()` and `load_chat_history()` in `chat_history_manager.py`

## Security Considerations

- **API keys**: Stored in `.streamlit/secrets.toml` (gitignored, 600 permissions)
- **No hardcoded credentials**: All secrets through Streamlit secrets API
- **Input validation**: API keys validated for minimum length (20 characters)
- **File permissions**: Secrets file automatically set to 600 (owner read/write only) on creation/modification
- **Sanitization**: Expert IDs and filenames sanitized to prevent path traversal

## Performance Guidelines

- **Use connection pooling**: Always use `get_cached_client()` from `client_pool.py` instead of creating new `LLMClient` instances
- **Leverage caching**: Expert configs cached with TTL; invalidate by incrementing `cache_version_{expert_id}` in session state
- **Pre-computed lookups**: Use utility functions from `constants.py` (`get_provider_config()`, `get_model_config()`, etc.) for O(1) access
- **Chat history limits**: 1MB file size limit enforced; old messages auto-trimmed when exceeded
- **Lazy loading**: Streamlit only loads active page; no need to implement additional lazy loading

## Git Workflow Notes

- **Permanent pages**: `pages/1000_Home.py` and `pages/9998_Settings.py` are committed to git
- **Generated pages**: `pages/1001_*.py` and higher are auto-generated; typically gitignored or regenerated via `setup.py`
- **Template changes**: After modifying `templates/template.py`, run `reset_application.py` and commit regenerated pages
- **Configurations**: Expert YAML configs in `configs/` are committed to git (contain prompts, not secrets)

## File Watching During Development

For faster development workflow:
```bash
streamlit run app.py --server.fileWatcherType=watchdog
```

Requires `watchdog` package (included in `requirements-dev.txt`). Provides instant reload when Python files change.

### Future

| Todo | Priority | Problem | Solution |
|------|----------|---------|----------|
| Review dead code cleanup | Low | ~290 lines of unused code identified | See `llm_comm/analysis/dead-code-analysis-2026-02-20.md` |
