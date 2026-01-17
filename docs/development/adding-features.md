# Adding Features Guide

This guide explains how to add new features to ExpertGPTs.

## Feature Development Guidelines

### 1. Follow DRY Principle

**Before writing code**:
- Search for existing implementations
- Extract shared functionality to utils
- Update ALL locations using duplicated code

**Example**: Adding a new form field
- If used in multiple places → Create utility function
- Update all locations
- Test thoroughly

### 2. Template-Based Changes

**When modifying expert page UI**:
1. Edit `templates/template.py`
2. Test with one expert
3. Run `reset_application.py` to regenerate all
4. Test multiple experts

**When modifying Home/Settings/Help**:
- Edit directly: `pages/1000_Home.py`, `pages/9998_Settings.py`, or `pages/9999_Help.py`
- No regeneration needed

### 3. Use Utility Modules

**Add to utils/** for:
- Shared business logic
- Reusable functions
- Common operations

**Example utility functions**:
- `utils/helpers.py`: Generic helpers
- `utils/config_manager.py`: Config operations
- `utils/llm_client.py`: LLM operations

## Common Feature Additions

### Adding a New Expert Page Feature

**Scenario**: Add "Export Chat" button to all expert pages

**Steps**:
1. Edit `templates/template.py`:
   ```python
   if st.button("Export Chat"):
       # Export logic
   ```

2. Test with one expert

3. Regenerate all expert pages:
   ```bash
   echo "yes" | python3 scripts/reset_application.py
   ```

4. Test multiple experts

### Adding a New Utility Function

**Scenario**: Add function to validate expert names

**Steps**:
1. Add to `utils/helpers.py`:
   ```python
   def validate_expert_name(name: str) -> bool:
       # Validation logic
       return True
   ```

2. Import and use in pages:
   ```python
   from utils.helpers import validate_expert_name

   if validate_expert_name(name):
       # Create expert
   ```

3. Write tests

4. Run tests to verify

### Adding a New LLM Provider

**Scenario**: Add support for "NewProvider" LLM

**Steps**:
1. Add provider config to `utils/constants.py`:
   ```python
   LLM_PROVIDERS["newprovider"] = {
       "name": "NewProvider",
       "base_url": "https://api.newprovider.com/v1",
       "default_model": "new-model",
       "models": {...}
   }
   ```

2. Update `utils/llm_client.py`:
   - Add thinking parameter handling
   - Support provider-specific features

3. Add API key UI in `pages/9998_Settings.py`

4. Update `.streamlit/secrets.toml.example`

5. Test with new provider

### Adding a New Language

**Scenario**: Add support for Japanese

**Steps**:
1. Add to `utils/i18n.py`:
   ```python
   LANGUAGE_METADATA["ja"] = {
       "name": "Japanese",
       "native_name": "日本語",
       "direction": "ltr"
   }
   ```

2. Create `locales/ui/ja.json` (copy from en.json)

3. Translate all strings

4. Add Japanese language names to all locale files

5. Test in app

### Adding a New Settings Option

**Scenario**: Add "Max Tokens" setting

**Steps**:
1. Add to `.streamlit/app_defaults.toml.example`:
   ```toml
   [llm]
   max_tokens = 4096
   ```

2. Update `utils/app_defaults_manager.py`:
   - Add `get_max_tokens_preference()`
   - Add `save_max_tokens_preference()`

3. Add UI in `pages/9998_Settings.py`:
   ```python
   max_tokens = st.slider("Max Tokens", 1, 8192, get_max_tokens_preference())
   if st.button("Save"):
       save_max_tokens_preference(max_tokens)
   ```

4. Test in app

## Code Organization

### Where to Put Code

**pages/**: UI and user interaction
- Home page: Expert management
- Settings: Configuration UI
- Expert pages: Chat interface (generated from template)

**utils/**: Business logic and utilities
- `config_manager.py`: Config operations
- `llm_client.py`: LLM API calls
- `page_generator.py`: Page generation
- `helpers.py`: Generic helpers
- `i18n.py`: Internationalization

**templates/**: Page templates
- `template.py`: Expert page template

**configs/**: Data
- Expert YAML configs

**scripts/**: Automation
- Setup, reset, maintenance

## Testing Your Changes

### 1. Write Tests First (TDD)

```python
# tests/test_my_feature.py
def test_my_new_feature():
    # Arrange
    input_data = {...}

    # Act
    result = my_function(input_data)

    # Assert
    assert result == expected
```

### 2. Run Tests

```bash
./scripts/run_tests.sh
```

### 3. Manual Testing

- Test with multiple experts
- Test in different browsers
- Test edge cases

## Committing Changes

### 1. Check Code Quality

```bash
# Format code
black .

# Run tests
./scripts/run_tests.sh
```

### 2. Write Clear Commit Messages

```bash
git add .
git commit -m "feat: add export chat button to expert pages

- Add export button to template
- Export chat history to JSON file
- Regenerate all expert pages"
```

### 3. Push Changes

```bash
git push
```

## Common Patterns

### Reading Expert Config

```python
from utils.config_manager import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config(expert_id)
name = config.get("expert_name")
description = config.get("description")
```

### Using i18n

```python
from utils.i18n import i18n

title = i18n.t("home.title")
button_text = i18n.t("buttons.add_chat")
```

### Getting Cached Client

```python
from utils.client_pool import get_cached_client
from utils.secrets_manager import SecretsManager

secrets_manager = SecretsManager()
api_key = secrets_manager.get_api_key(provider)
client = get_cached_client(provider, api_key)
```

## Related Documentation

- **[Development Setup](setup.md)** - Development environment
- **[Project Structure](project-structure.md)** - File organization
- **[Template System](../architecture/template-system.md)** - Template-based pages

---

**Back to**: [Documentation Home](../README.md) | [Development Setup](setup.md)
