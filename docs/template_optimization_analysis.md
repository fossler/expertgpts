# Template Optimization Analysis

**Date:** 2026-01-01
**Analyzed File:** `templates/template.py`
**Focus Areas:** DRY, Code Simplification, Performance, Structure

---

## User Prompt

> Use deep thinking to examine this page for potential optimizations. Focus on:
>
> - DRY
> - Code optimization for simplification
> - Code optimization for performance improvement
> - Structural optimizations

---

## Analysis Summary

This document provides a comprehensive optimization analysis of `templates/template.py`, the core template used to generate all expert agent pages in ExpertGPTs. The analysis identifies opportunities across code quality, performance, and architectural dimensions.

---

## 1. DRY Violations ✅ **COMPLETED** 🔴 Critical Priority

**Status:** Fixed in commit `f079b42` (2026-01-01)

### Issue 1.1: Duplicate API Key Initialization ✅ **FIXED**

**Severity:** HIGH (Resolved)
**Files Affected:**
- `templates/template.py:20-37`
- `app.py:15-30`
- `templates/9999_Settings.py:16-?`

**Current Implementation:**
```python
def initialize_session_state():
    """Initialize session state variables."""
    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Initialize API key in session state (from secrets or existing session)
    if "deepseek_api_key" not in st.session_state:
        # Try to get from st.secrets first (Streamlit's recommended way)
        try:
            secrets_api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
            st.session_state.deepseek_api_key = secrets_api_key or ""
        except Exception:
            # If secrets.toml doesn't exist or has errors, initialize as empty
            st.session_state.deepseek_api_key = ""

    return messages_key
```

**Impact:** 6-9 lines of duplicate code across multiple files, making maintenance harder and increasing bug risk.

**Recommended Solution:**
Create `utils/session_state.py`:
```python
"""Session state management utilities."""

import streamlit as st


def initialize_shared_session_state():
    """Initialize shared session state variables across all pages.

    This function should be called once at app startup to initialize
    session state variables that are shared across all pages.
    """
    if "deepseek_api_key" not in st.session_state:
        try:
            secrets_api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
            st.session_state.deepseek_api_key = secrets_api_key or ""
        except Exception:
            st.session_state.deepseek_api_key = ""
```

Then update `templates/template.py`:
```python
from utils.session_state import initialize_shared_session_state


def initialize_session_state():
    """Initialize session state variables."""
    # Initialize shared state first
    initialize_shared_session_state()

    # Initialize messages key for this specific expert
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    return messages_key
```

### Issue 1.2: Unused Imports ✅ **FIXED**

**Lines:** 7, 12

```python
import os  # Line 7 - NEVER USED
from utils import secrets_manager  # Line 12 - NEVER USED (using st.secrets directly)
```

**Fix:** Remove both lines.

---

## 2. Code Simplification ✅ **COMPLETED** 🟡 Medium Priority

**Status:** Fixed in commit on 2026-01-01

### Simplification 2.1: Token Counting Loop ✅ **FIXED**

**Current (lines 222-224):**
```python
messages_tokens = 0
for message in messages:
    messages_tokens += count_tokens(message.get("content", ""), encoding)
```

**Optimized:**
```python
messages_tokens = sum(
    count_tokens(msg.get("content", ""), encoding)
    for msg in messages
)
```

**Benefits:**
- More Pythonic
- 3 lines → 1 line
- Generator expression is memory efficient

### Simplification 2.2: Config Validation ✅ **FIXED**

**Current (lines 264-266):**
```python
if not config:
    st.error("Failed to load expert configuration.")
    return
```

**Improved:**
```python
if not config:
    st.error(f"Configuration not found for expert: {EXPERT_ID}")
    st.stop()  # More explicit than return
```

**Benefits:**
- More specific error message with EXPERT_ID
- `st.stop()` is more explicit than `return` in Streamlit

---

## 3. Performance Optimizations ✅ **COMPLETED** 🟢 Low-Medium Priority

**Status:** Fixed in commit on 2026-01-01
**Implemented:** Option A - Cache with @st.cache_data

### Performance 3.1: Token Counting on Every Rerun ✅ **FIXED**

**Current Behavior (lines 221-224):**
Token counts are recalculated on every rerun, even when messages haven't changed.

**Optimization Option A: Cache with @st.cache_data** (Recommended)

```python
@st.cache_data(ttl=60, show_spinner=False)
def count_messages_tokens(messages_key: str, messages: list) -> int:
    """Count tokens in chat messages (cached for 60 seconds)."""
    encoding = get_encoding()
    return sum(
        count_tokens(msg.get("content", ""), encoding)
        for msg in messages
    )
```

**Usage in `display_context_usage()`:**
```python
# Count tokens in chat messages
messages = st.session_state.get(messages_key, [])
messages_tokens = count_messages_tokens(messages_key, messages)
```

**Optimization Option B: Store Token Count in Message Metadata** (Advanced)

```python
# When adding user message (line 114)
st.session_state[messages_key].append({
    "role": "user",
    "content": prompt,
    "tokens": count_tokens(prompt, encoding)  # Cache once
})

# When adding assistant response (line 147)
st.session_state[messages_key].append({
    "role": "assistant",
    "content": response,
    "tokens": count_tokens(response, encoding)  # Cache once
})

# Then in display_context_usage() - just sum the cached values
messages_tokens = sum(
    msg.get("tokens", 0)
    for msg in st.session_state.get(messages_key, [])
)
```

**Recommendation:** Start with **Option A** for simplicity. Only implement Option B if profiling shows this is a bottleneck.

### Performance 3.2: System Prompt Token Counting ✅ **FIXED**

**Current (line 218):**
```python
system_tokens = count_tokens(system_prompt, encoding) if system_prompt else 0
```

**Optimized:**
```python
@st.cache_data(ttl=300)
def count_system_prompt_tokens(system_prompt: str) -> int:
    """Count tokens in system prompt (cached for 5 minutes)."""
    if not system_prompt:
        return 0
    encoding = get_encoding()
    return count_tokens(system_prompt, encoding)

# Usage:
system_tokens = count_system_prompt_tokens(config.get("system_prompt", ""))
```

**Benefits:**
- System prompts rarely change within a session
- Avoids redundant token counting on every rerun

---

## 4. Structural Optimizations 🔵 Medium Priority

### Structure 4.1: Centralize Constants

**Current:** Magic numbers scattered throughout the code

```python
# Line 230
max_tokens = 128000

# Lines 237-244
if usage_percent < 50:
    color = "🟢"
elif usage_percent < 75:
    color = "🟡"
elif usage_percent < 90:
    color = "🟠"
```

**Solution:** Create `utils/constants.py`:

```python
"""Application-wide constants."""

# DeepSeek API Constants
DEEPSEEK_MAX_CONTEXT_TOKENS = 128000
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 1.0

# Context Usage Thresholds (percentages)
CONTEXT_USAGE_SAFE_THRESHOLD = 50
CONTEXT_USAGE_WARNING_THRESHOLD = 75
CONTEXT_USAGE_ALERT_THRESHOLD = 90

# Context Usage Colors
CONTEXT_USAGE_COLORS = {
    "safe": "🟢",
    "warning": "🟡",
    "alert": "🟠",
    "critical": "🔴"
}

# Cache TTLs (seconds)
CONFIG_CACHE_TTL = 300
TOKEN_COUNT_CACHE_TTL = 60
```

**Usage in template.py:**
```python
from utils.constants import (
    DEEPSEEK_MAX_CONTEXT_TOKENS,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS
)

# In display_context_usage():
max_tokens = DEEPSEEK_MAX_CONTEXT_TOKENS

if usage_percent < CONTEXT_USAGE_SAFE_THRESHOLD:
    color = CONTEXT_USAGE_COLORS["safe"]
elif usage_percent < CONTEXT_USAGE_WARNING_THRESHOLD:
    color = CONTEXT_USAGE_COLORS["warning"]
# ...
```

### Structure 4.2: Extract Token Management to Utility

**Current:** Token logic mixed with UI code (lines 176-254)

**Solution:** Create `utils/token_manager.py`:

```python
"""Token counting and context usage management for DeepSeek API."""

import streamlit as st
import tiktoken
from utils.constants import (
    DEEPSEEK_MAX_CONTEXT_TOKENS,
    CONTEXT_USAGE_ALERT_THRESHOLD,
    CONTEXT_USAGE_WARNING_THRESHOLD,
    CONTEXT_USAGE_SAFE_THRESHOLD,
    CONTEXT_USAGE_COLORS
)


class TokenManager:
    """Manages token counting and context usage for DeepSeek API."""

    @staticmethod
    @st.cache_resource
    def get_encoding():
        """Get and cache the tiktoken encoding for DeepSeek.

        Uses cl100k_base encoding (same as GPT-3.5/4).

        Returns:
            Tiktoken encoding object
        """
        return tiktoken.get_encoding("cl100k_base")

    @staticmethod
    def count_tokens(text: str, encoding=None) -> int:
        """Count tokens in a text string.

        Args:
            text: Text to count tokens for
            encoding: Optional pre-loaded encoding (for batch processing)

        Returns:
            Number of tokens
        """
        if encoding is None:
            encoding = TokenManager.get_encoding()
        return len(encoding.encode(text))

    @staticmethod
    def calculate_usage_statistics(
        system_prompt: str,
        messages: list,
        max_tokens: int = DEEPSEEK_MAX_CONTEXT_TOKENS
    ) -> dict:
        """Calculate comprehensive token usage statistics.

        Args:
            system_prompt: System prompt text
            messages: List of chat messages
            max_tokens: Maximum context window size

        Returns:
            Dictionary with usage statistics:
            {
                "total_tokens": int,
                "usage_percent": float,
                "system_tokens": int,
                "messages_tokens": int,
                "color": str (emoji)
            }
        """
        try:
            encoding = TokenManager.get_encoding()
        except Exception:
            return {
                "error": "Token counting unavailable",
                "total_tokens": 0,
                "usage_percent": 0
            }

        # Count tokens in system prompt
        system_tokens = (
            TokenManager.count_tokens(system_prompt, encoding)
            if system_prompt else 0
        )

        # Count tokens in chat messages
        messages_tokens = sum(
            TokenManager.count_tokens(msg.get("content", ""), encoding)
            for msg in messages
        )

        # Calculate totals
        total_tokens = system_tokens + messages_tokens
        usage_percent = (total_tokens / max_tokens) * 100

        # Determine color based on usage
        if usage_percent < CONTEXT_USAGE_SAFE_THRESHOLD:
            color = CONTEXT_USAGE_COLORS["safe"]
        elif usage_percent < CONTEXT_USAGE_WARNING_THRESHOLD:
            color = CONTEXT_USAGE_COLORS["warning"]
        elif usage_percent < CONTEXT_USAGE_ALERT_THRESHOLD:
            color = CONTEXT_USAGE_COLORS["alert"]
        else:
            color = CONTEXT_USAGE_COLORS["critical"]

        return {
            "total_tokens": total_tokens,
            "usage_percent": usage_percent,
            "system_tokens": system_tokens,
            "messages_tokens": messages_tokens,
            "color": color,
            "max_tokens": max_tokens
        }

    @staticmethod
    def format_usage_stats(stats: dict) -> str:
        """Format usage statistics for display.

        Args:
            stats: Statistics dictionary from calculate_usage_statistics()

        Returns:
            Formatted string
        """
        if "error" in stats:
            return stats["error"]

        return (
            f"{stats['color']} **{stats['usage_percent']:.1f}%** "
            f"of {stats['max_tokens']:,} tokens\n"
            f"Total: {stats['total_tokens']:,} / {stats['max_tokens']:,} tokens"
        )
```

**Updated `display_context_usage()` in template.py:**
```python
from utils.token_manager import TokenManager


def display_context_usage(config: dict, messages_key: str):
    """Display context length usage in the sidebar.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # Calculate usage statistics
    system_prompt = config.get("system_prompt", "")
    messages = st.session_state.get(messages_key, [])

    stats = TokenManager.calculate_usage_statistics(system_prompt, messages)

    # Display context usage in sidebar
    st.sidebar.markdown("### 📊 Context Usage")

    if "error" in stats:
        st.sidebar.caption(f"ℹ️ {stats['error']}")
        return

    # Display main stats
    st.sidebar.markdown(TokenManager.format_usage_stats(stats))

    # Show breakdown
    with st.sidebar.expander("See breakdown"):
        st.caption(
            f"📝 System Prompt: {stats['system_tokens']:,} tokens"
        )
        st.caption(
            f"💬 Chat Messages: {stats['messages_tokens']:,} tokens"
        )

    st.sidebar.divider()
```

### Structure 4.3: Separate UI from Business Logic

**Current:** `display_context_usage()` mixes calculation with display.

**Solution:** Already addressed in Structure 4.2 - `TokenManager` handles pure business logic, `display_context_usage()` handles pure UI.

---

## 5. Error Handling Improvements 🟡 Medium Priority

### Error 5.1: Generic Exception Handling

**Current (lines 209-214):**
```python
try:
    encoding = get_encoding()
except Exception:
    # Fallback if tiktoken fails
    st.sidebar.caption("ℹ️ Token counting unavailable")
    return
```

**Improved:**
```python
try:
    encoding = get_encoding()
except (ImportError, OSError, ValueError) as e:
    # Fallback if tiktoken fails
    st.sidebar.caption(f"ℹ️ Token counting unavailable: {str(e)}")
    return
```

**Benefits:**
- More specific error types
- Better debugging with error message
- Avoids catching unexpected exceptions

### Error 5.2: API Key Validation

**Current:** API key format not validated until API call (line 126).

**Improved:** Add early validation:
```python
def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate API key format before using.

    Args:
        api_key: API key to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is not set"

    if len(api_key) < 20:
        return False, "API key appears to be invalid (too short)"

    # DeepSeek API keys typically start with "sk-"
    if not api_key.startswith("sk-"):
        return False, "API key format is invalid (should start with 'sk-')"

    return True, ""


# In handle_user_input():
is_valid, error_msg = validate_api_key(api_key)
if not is_valid:
    st.error(f"❌ {error_msg}. Please check your Settings.")
    return
```

### Error 5.3: Configuration Loading

**Current (lines 71-73):**
```python
if not config:
    st.error(f"Configuration not found for expert: {EXPERT_ID}")

return config
```

**Improved:**
```python
if not config:
    st.error(
        f"❌ Configuration not found for expert: {EXPERT_ID}\n\n"
        f"This expert may have been deleted. Please return to Home."
    )
    st.stop()

return config
```

---

## 6. Type Safety & Documentation 🟢 Nice-to-Have

### Add Type Hints

**Before:**
```python
def load_expert_config() -> dict:
    """Load the expert configuration with cache support."""
    # ...
```

**After:**
```python
from typing import Dict, List, Optional, Tuple


def load_expert_config() -> Dict:
    """Load the expert configuration with cache support.

    Returns:
        Configuration dictionary with keys:
        - expert_id: str
        - expert_name: str
        - description: str
        - temperature: float
        - system_prompt: Optional[str]
    """
    # ...


def render_chat_interface(config: Dict, messages_key: str) -> None:
    """Render the main chat interface.

    Args:
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # ...


def handle_user_input(api_key: str, config: Dict, messages_key: str) -> None:
    """Handle user input and generate assistant response.

    Args:
        api_key: DeepSeek API key
        config: Expert configuration dictionary
        messages_key: Session state key for this expert's messages
    """
    # ...
```

### Add Docstring Standards

Use Google-style docstrings consistently:

```python
def count_tokens(text: str, encoding) -> int:
    """Count tokens in a text string.

    Args:
        text: Text to count tokens for
        encoding: Tiktoken encoding object

    Returns:
        Number of tokens in the text

    Example:
        >>> encoding = tiktoken.get_encoding("cl100k_base")
        >>> count_tokens("Hello, world!", encoding)
        4
    """
    return len(encoding.encode(text))
```

---

## Priority Summary

| Priority | Category | Issue | Impact | Effort | ROI |
|----------|----------|-------|--------|--------|-----|
| 🔴 CRITICAL | DRY | Duplicate `initialize_session_state()` | High maintainability burden | Medium | **High** |
| 🔴 CRITICAL | DRY | Remove unused imports | Code clarity | Low | **High** |
| 🟡 HIGH | Simplification | Simplify token counting loop | Readability | Low | **Medium** |
| 🟡 HIGH | Structure | Centralize constants | Maintainability | Low | **Medium** |
| 🟡 HIGH | Error Handling | Better exception handling | Debugging | Medium | **Medium** |
| 🟢 MEDIUM | Performance | Cache token counts | Potential speedup | Low-Medium | **Medium** |
| 🟢 MEDIUM | Structure | Extract TokenManager class | Testability | High | **Low** |
| 🔵 LOW | Quality | Add type hints | IDE support | Medium | **Low** |
| 🔵 LOW | Quality | Separate UI from logic | Testability | High | **Low** |

---

## Recommended Action Plan

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Remove unused imports (`os`, `secrets_manager`)
2. ✅ Simplify token counting loop using `sum()`
3. ✅ Create `utils/constants.py` with magic numbers
4. ✅ Extract shared session state initialization to `utils/session_state.py`

**Expected Benefits:**
- Cleaner code
- Better maintainability
- Single source of truth for session state

### Phase 2: Performance & Structure (3-4 hours)
5. ✅ Cache token counting operations with `@st.cache_data`
6. ✅ Create `utils/token_manager.py` for token management
7. ✅ Improve error handling with specific exceptions
8. ✅ Add API key validation

**Expected Benefits:**
- Reduced redundant computations
- Better error messages
- Improved code organization

### Phase 3: Architecture (Future / Nice-to-Have)
9. ⏸️ Separate UI from business logic completely
10. ⏸️ Add comprehensive type hints throughout
11. ⏸️ Consider token metadata in message structure (if profiling shows need)

**Expected Benefits:**
- Better testability
- Improved IDE support
- Potential performance gains

---

## Implementation Notes

### Before Implementing:
1. **Run tests:** `pytest` to ensure current state passes
2. **Profile app:** Use `st.sandbox` or similar to identify actual bottlenecks
3. **Backup:** Consider creating a branch for optimizations

### During Implementation:
1. **One change at a time:** Commit after each optimization
2. **Test thoroughly:** Verify app still works after each change
3. **Document:** Update CLAUDE.md with any architectural changes

### After Implementation:
1. **Run full test suite:** `pytest -v`
2. **Manual testing:** Test chat functionality with multiple experts
3. **Performance comparison:** Measure before/after if performance was goal

---

## Conclusion

The `templates/template.py` file is well-structured overall but has opportunities for improvement in:

1. **DRY compliance** - Highest priority due to maintainability impact
2. **Code simplification** - Quick wins that improve readability
3. **Performance** - Moderate improvements through caching
4. **Architecture** - Long-term benefits through better separation of concerns

**Recommendation:** Start with **Phase 1 optimizations** as they provide immediate benefits with minimal risk. Progress to Phase 2 if profiling indicates performance needs. Consider Phase 3 as part of future refactoring efforts.

---

**Generated by:** Claude Code (Claude Sonnet 4.5)
**Analysis Date:** 2026-01-01
