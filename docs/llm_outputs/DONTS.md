# DON'Ts: Lessons Learned from ExpertGPTs Development

This file documents common pitfalls and mistakes to avoid when working with Streamlit and this codebase.

## Streamlit Caching

### ❌ DON'T: Use @st.cache_resource on instance methods without leading underscore

```python
# WRONG - This will cause UnhashableParamError
class PageGenerator:
    @st.cache_resource
    def _build_page_index(self):  # Streamlit tries to hash self
        pass
```

**Why it fails:** Streamlit tries to hash all parameters (including `self`) to create a cache key. Objects with functions cannot be hashed.

### ✅ DO: Use leading underscore for instance parameters

```python
# CORRECT - Leading underscore tells Streamlit to skip hashing
class PageGenerator:
    @st.cache_resource
    def _build_page_index(_self):  # Streamlit skips _self from hashing
        pass
```

**Why it works:** The leading underscore tells Streamlit "this is an internal parameter, don't include it in the cache key." Python still passes `self` automatically when called as `self._build_page_index()`.

### ❌ DON'T: Forget to invalidate cache when data changes

```python
# WRONG - Cache doesn't know new pages were created
@st.cache_resource
def _build_page_index(_self):
    pages = list(_self.pages_dir.glob("*.py"))
    return pages

# Later: Create a new page
page_generator.generate_page(...)
st.rerun()  # Cache still returns old page list!
```

**Why it fails:** `@st.cache_resource` persists across reruns. Creating new files doesn't automatically invalidate the cache, so the navigation system tries to switch to a page that isn't registered.

### ✅ DO: Manually clear cache after mutations

```python
# CORRECT - Clear cache after mutations
class PageGenerator:
    @st.cache_resource
    def _build_page_index(_self):
        pages = list(_self.pages_dir.glob("*.py"))
        return pages

    def clear_page_cache(self):
        """Clear the cached page index."""
        _build_page_index.clear()  # Invalidate the cache

# Later: Create a new page and clear cache
page_generator.generate_page(...)
page_generator.clear_page_cache()  # Force rebuild on next access
st.rerun()  # Navigation will see updated page list
```

**Why it works:** Calling `function_name.clear()` invalidates the cache, so the next call rebuilds the data with fresh files.

### ❌ DON'T: Assume cached data is always in sync with filesystem

```python
# WRONG - Crashes if page file was deleted
page_list = page_generator.list_pages()  # May return stale data
for page_info in page_list:
    page_path = Path("pages") / page_info["filename"]
    pages.append(st.Page(str(page_path)))  # Crashes if file doesn't exist!
```

**Why it fails:** Even with cache clearing, there can be timing issues or race conditions where the cached list doesn't immediately reflect filesystem changes. The app crashes trying to create `st.Page()` for a deleted file.

### ✅ DO: Add defensive checks for filesystem state

```python
# CORRECT - Verify files exist before using them
page_list = page_generator.list_pages()
for page_info in page_list:
    page_path = Path("pages") / page_info["filename"]

    # Skip if page file doesn't exist (may have been deleted)
    if not page_path.exists():
        continue

    pages.append(st.Page(str(page_path)))  # Safe: file exists
```

**Why it works:** Even if the page list is stale, we verify each file exists before creating a page object. This makes the app resilient to cache timing issues and race conditions.

### ❌ DON'T: Forget imports used in cached methods

```python
# WRONG - Uses re.match() but no import
class PageGenerator:
    @st.cache_resource
    def _build_page_index(_self):
        match = re.match(r"(\d+)_(.+)\.py", filename)  # NameError: name 're' is not defined
```

### ✅ DO: Import all modules at the top of the file

```python
# CORRECT
import re
from pathlib import Path

class PageGenerator:
    @st.cache_resource
    def _build_page_index(_self):
        match = re.match(r"(\d+)_(.+)\.py", filename)
```

## Code Duplication (DRY Violations)

### ❌ DON'T: Copy-paste validation logic across files

```python
# WRONG - Duplicated in multiple files
if not expert_name or len(expert_name) > 100:
    raise ValueError("Invalid expert name")
```

### ✅ DO: Use centralized validation utilities

```python
# CORRECT - Use shared validators
from utils.validators import validate_expert_name

expert_name = validate_expert_name(expert_name)
```

### ❌ DON'T: Repeat session state initialization patterns

```python
# WRONG - Duplicated in every page
if f"messages_{EXPERT_ID}" not in st.session_state:
    st.session_state[f"messages_{EXPERT_ID}"] = []
```

### ✅ DO: Use centralized session state utilities

```python
# CORRECT - Use shared session state functions
from utils.session_state import initialize_expert_session_state

initialize_expert_session_state(EXPERT_ID)
```

## Performance

### ❌ DON'T: Read file contents for simple metadata

```python
# WRONG - Slow: Reads entire file just to get expert name
for page_file in pages_dir.glob("*.py"):
    with open(page_file) as f:
        content = f.read()
        expert_name = extract_from_content(content)
```

### ✅ DO: Parse filenames when possible

```python
# CORRECT - Fast: Just parses filename
for page_file in pages_dir.glob("*.py"):
    match = re.match(r"(\d+)_(.+)\.py", page_file.name)
    expert_name = match.group(2).replace("_", " ").title()
```

### ❌ DON'T: Traverse nested dictionaries repeatedly

```python
# WRONG - Slow: O(n) lookup every time
provider_name = LLM_PROVIDERS[provider]["name"]
model_name = LLM_PROVIDERS[provider]["models"][model_id]["name"]
```

### ✅ DO: Use pre-computed lookup tables

```python
# CORRECT - Fast: O(1) direct access
provider_name = PROVIDER_NAMES[provider]
model_name = MODEL_LOOKUP[provider][model_id]["name"]
```

## Error Handling

### ❌ DON'T: Use generic exceptions everywhere

```python
# WRONG - Uninformative
raise ValueError("Something went wrong")
```

### ✅ DO: Use specific custom exceptions

```python
# CORRECT - Clear and categorizable
from utils.exceptions import ValidationError, APIError, ConfigurationError

raise ValidationError("Invalid expert name: too long")
```

### ❌ DON'T: Catch all exceptions silently

```python
# WRONG - Hides bugs
try:
    risky_operation()
except Exception:
    pass  # Silent failure
```

### ✅ DO: Log errors and provide context

```python
# CORRECT - Observable and debuggable
from utils.logging import get_logger
from utils.exceptions import ExpertGPTsError

logger = get_logger(__name__)

try:
    risky_operation()
except ExpertGPTsError as e:
    logger.log_error("ConfigurationError", str(e), {"file": config_path})
    raise
```

## API Key Management

### ❌ DON'T: Store API keys in session state only

```python
# WRONG - Lost on refresh
st.session_state.api_key = user_input
```

### ✅ DO: Persist to .streamlit/secrets.toml

```python
# CORRECT - Survives refreshes
from utils.secrets_manager import save_api_key

save_api_key(user_input)  # Persists to file with secure permissions
```

### ❌ DON'T: Commit API keys to git

```python
# NEVER DO THIS - Security risk
# In secrets.toml (committed to git):
DEEPSEEK_API_KEY = "sk-1234567890"
```

### ✅ DO: Keep secrets.toml in .gitignore

```bash
# .gitignore
.streamlit/secrets.toml
```

## Type Safety

### ❌ DON'T: Skip type hints for utility functions

```python
# WRONG - Hard to understand and refactor
def get_expert_setting(expert_id, setting, default=None):
    return st.session_state.get(f"{setting}_{expert_id}", default)
```

### ✅ DO: Add comprehensive type hints

```python
# CORRECT - Self-documenting and IDE-friendly
from typing import Optional, Any

def get_expert_setting(
    expert_id: str,
    setting: str,
    default: Optional[Any] = None
) -> Optional[Any]:
    """Get a session state setting for a specific expert."""
    setting_key = f"{setting}_{expert_id}"
    return st.session_state.get(setting_key, default)
```

## Testing

### ❌ DON'T: Write tests that modify project files

```python
# WRONG - Pollutes project
def test_create_page():
    pg = PageGenerator()
    pg.generate_page("test_id", "Test Expert")  # Creates in pages/
```

### ✅ DO: Use temporary directories

```python
# CORRECT - Isolated and clean
import pytest

def test_create_page(tmp_path):
    pg = PageGenerator(pages_dir=tmp_path)
    pg.generate_page("test_id", "Test Expert")  # Creates in temp dir
    # pytest auto-cleanup
```

## File Naming Conventions

### ❌ DON'T: Use inconsistent naming patterns

```python
# WRONG - Hard to discover and remember
utils/validation.py
utils/session.py
utils/pageGen.py
```

### ✅ DO: Use descriptive, consistent names

```python
# CORRECT - Easy to find and understand
utils/validators.py
utils/session_state.py
utils/page_generator.py
```

## Summary Checklist

Before committing code, verify:

- [ ] No DRY violations (search for similar patterns first)
- [ ] All cached methods use leading underscore for instance parameters
- [ ] All imports are present at the top of the file
- [ ] Type hints added to utility functions
- [ ] Custom exceptions used instead of generic ValueError
- [ ] Performance optimizations applied (lookup tables, index-based discovery)
- [ ] API keys never committed to git
- [ ] Tests use temporary directories
- [ ] Error messages are specific and actionable
- [ ] Session state uses shared utilities

---

**Remember:** This file is a living document. Add new lessons learned as you discover them.
