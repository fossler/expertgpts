# Template System Guide

This guide explains ExpertGPTs' template-based architecture for generating expert pages.

## Overview

ExpertGPTs uses a **master template** (`templates/template.py`) to generate all expert pages. This ensures consistent UI/UX across all experts while maintaining the DRY principle.

## How It Works

### Template-Based Generation Process

```
┌─────────────────────────────────────────────────────────────┐
│  1. User creates expert via UI (Home page)                  │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PageGenerator generates unique expert ID                │
│     Example: "1005_sql_expert"                              │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Expert config created (configs/1005_sql_expert.yaml)    │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Template read (templates/template.py)                   │
│     Contains placeholders: {{EXPERT_ID}}, {{EXPERT_NAME}}   │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Placeholders replaced with expert-specific values       │
│     {{EXPERT_ID}} → 1005_sql_expert                         │
│     {{EXPERT_NAME}} → SQL Expert                            │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Expert page generated (pages/1005_sql_expert.py)        │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  7. Navigation to new expert page                           │
└─────────────────────────────────────────────────────────────┘
```

## Template Structure

### Template File

**Location**: `templates/template.py`

**Purpose**: Master template for all expert pages

**Placeholders**:
- `{{EXPERT_ID}}` - Unique expert identifier
- `{{EXPERT_NAME}}` - Display name of the expert

### Example Template Structure

```python
# templates/template.py (excerpt)

import streamlit as st
from lib.config.config_manager import get_config_manager, get_llm_metadata
from lib.shared.session_state import initialize_shared_session_state
from lib.i18n import i18n
from lib.storage import load_chat_history, save_chat_history, StreamingCache
from lib.ui.chat_toolbox import render_chat_toolbox, render_user_message

# Expert Configuration
EXPERT_ID = "{{EXPERT_ID}}"
EXPERT_NAME = "{{EXPERT_NAME}}"


def initialize_session_state():
    initialize_shared_session_state()
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = load_chat_history(EXPERT_ID)
    return messages_key

# ... load_expert_config(), render_chat_interface(), handle_user_input(), main()
```

`st.set_page_config()` is not called in the template; `app.py` sets the page configuration once before `st.navigation()`.

### Generated Expert Page

**Location**: `pages/{expert_id}.py`

**Example**: `pages/1005_sql_expert.py`

After placeholder replacement only the two constants differ from the template:
```python
# pages/1005_sql_expert.py

# Expert Configuration
EXPERT_ID = "1005_sql_expert"
EXPERT_NAME = "SQL Expert"

# ... rest identical to templates/template.py
```

## Page Numbering Scheme

### Reserved Numbers

| Number | Page | Type | Description |
|--------|------|------|-------------|
| **1000** | Home | Permanent | Expert list and management |
| **1001-9997** | Experts | Generated | Individual expert pages |
| **9998** | Settings | Permanent | App settings and configuration |
| **9999** | Help | Permanent | Documentation viewer |

### Expert ID Generation

**Format**: `{number}_{sanitized_name}`

**Examples**:
- `1001_python_expert`
- `1002_data_scientist`
- `1005_sql_expert`
- `1010_career_coach`

**Sanitization Rules**:
- Unicode NFC normalization, convert to lowercase
- Replace spaces/hyphens with underscores
- Remove special characters
- Limit to alphanumeric and underscores, max 64 characters, no leading/trailing underscores

**Implementation**: `lib/shared/helpers.py` - `sanitize_name()` function

## Regenerating Expert Pages

### When to Regenerate

**Regenerate all expert pages when**:
- You modify `templates/template.py`
- You add new features to expert pages
- You fix bugs in expert page logic
- You update UI/UX patterns

**Do NOT regenerate when**:
- You only edit Home or Settings pages (they're permanent)
- You only modify expert YAML configs
- You only change utility functions

### Regeneration Process

**Via Script**:
```bash
uv run python scripts/regenerate_pages.py
```

**What Happens** (`PageGenerator.regenerate_pages()` in `lib/shared/page_generator.py`):
1. Finds all existing expert pages in `pages/` (system pages such as `1000_Home.py`, `9998_Settings.py`, `9999_Help.py` and `_`-prefixed pages are skipped)
2. Reads each page's `EXPERT_ID` and `EXPERT_NAME`
3. Rewrites the page from `templates/template.py` with the same filename, ID and name

Expert configs (`configs/`), chat history (`chat_history/`) and chat images (`chat_attachments/`) are not touched and stay attached to their pages.

**Warning**: Custom edits to individual expert pages will be lost, because each page is overwritten with the template.

**Generated pages are local**: Expert pages (`pages/1001_*.py` and higher) are gitignored, so only `templates/template.py` is committed. After pulling a template change on another machine, run `regenerate_pages.py` there as well.

**Not for template changes**: `scripts/reset_application.py` deletes all configs, pages, chat history, chat images and the streaming cache and recreates the example experts. Use it only when you want a full reset.

**Best Practice**: Keep all expert-specific logic in the template or in YAML configs. Never edit generated expert pages directly.

## Permanent vs. Generated Pages

### Permanent Pages

**Home Page** (`pages/1000_Home.py`):
- Not generated from template
- Manually maintained
- Contains expert management UI
- "Add Chat" functionality

**Settings Page** (`pages/9998_Settings.py`):
- Not generated from template
- Manually maintained
- Settings for API keys, theme, language, defaults

**Help Page** (`pages/9999_Help.py`):
- Not generated from template
- Manually maintained
- Displays documentation from `docs/` directory

**Characteristics**:
- Committed to git
- Edited directly
- Not affected by `regenerate_pages.py` or `reset_application.py`

### Generated Expert Pages

**Expert Pages** (`pages/1001_*.py` to `pages/9997_*.py`):
- Generated from template
- Auto-generated, not manually edited
- Regenerated via `regenerate_pages.py`

**Characteristics**:
- Gitignored (local to each installation)
- Should NOT be manually edited
- Always regenerate from template

## Modifying the Template

### Adding New Features to All Experts

**Workflow**:
1. Edit `templates/template.py`
2. Test with one expert first
3. Run `uv run python scripts/regenerate_pages.py` to regenerate all
4. Test multiple experts to verify
5. Commit changes

**Example**: Add "Export Chat" button to all expert pages

```python
# In templates/template.py

# Add export button
if st.button("Export Chat"):
    chat_history = st.session_state[f"messages_{EXPERT_ID}"]
    # Export logic here
```

Then regenerate:
```bash
uv run python scripts/regenerate_pages.py
```

All expert pages now have the export button.

### Template Modification Best Practices

**DO ✅**:
- Test changes with one expert before regenerating all
- Keep template modular and readable
- Add comments for complex logic
- Follow DRY principle within template
- Use utility functions for common operations

**DON'T ❌**:
- Edit generated expert pages directly
- Skip testing before regenerating
- Make breaking changes without considering existing experts
- Hardcode values that should be in YAML configs

## Template Components

### Expert Config Loading

```python
@st.cache_data(ttl=CONFIG_CACHE_TTL, show_spinner="Loading expert configuration...")
def load_expert_config_cached(expert_id: str, cache_version: int = 0) -> dict:
    config_manager = get_config_manager()
    try:
        return config_manager.load_config(expert_id)
    except FileNotFoundError:
        return {}


def load_expert_config() -> dict:
    cache_version = st.session_state.get(f"cache_version_{EXPERT_ID}", 0)
    return load_expert_config_cached(EXPERT_ID, cache_version)
```

Provider, model and thinking level come from the config metadata: `provider, model, thinking_level = get_llm_metadata(config)`.

### Session State Initialization

```python
def initialize_session_state():
    # Shared state first (API keys, defaults, language)
    initialize_shared_session_state()

    # Messages history, loaded from chat_history/{EXPERT_ID}.json on first run
    messages_key = f"messages_{EXPERT_ID}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = load_chat_history(EXPERT_ID)

    return messages_key
```

Provider, model, temperature and thinking level are not kept in session state; the toolbox model row writes them directly to the expert config.

### Chat Interface

```python
# Display chat history (assistant avatar per message; user messages show
# image thumbnails and text attachments as expanders)
provider, _, _ = get_llm_metadata(config)
for message in st.session_state[messages_key]:
    if message["role"] == "assistant":
        avatar = get_provider_avatar(message.get("provider") or provider)
        with st.chat_message("assistant", avatar=avatar):
            st.markdown(sanitize_markdown_content(message["content"]))
    else:
        with st.chat_message("user"):
            render_user_message(message["content"])

# Chat input with the toolbox pinned below it (handle_user_input())
with st.bottom:
    prompt = st.chat_input(i18n.t("home.chat_input_placeholder"))
    toolbox = render_chat_toolbox(
        f"{attachments_key}_{attachments_generation}", config, EXPERT_ID, messages_key
    )

# A transcribed voice message is sent like a typed prompt
prompt = prompt or toolbox.voice_prompt
if prompt:
    # Store images on disk, embed references and text files into the message
    image_refs = [
        (name, save_image(EXPERT_ID, name, data)) for name, data in toolbox.images
    ]
    content = build_message_content(prompt, toolbox.attachments, image_refs)

    # Add user message to history
    st.session_state[messages_key].append({"role": "user", "content": content})
    save_chat_history(EXPERT_ID, st.session_state[messages_key])

    # Generate response: image tags become image parts (or a text note)
    images_supported = supports_images(provider, model)
    api_messages = [
        {"role": m["role"], "content": to_api_content(m["content"], images_supported)}
        for m in st.session_state[messages_key]
    ]
    # ... background streaming via StreamingCache, see background-streaming.md ...

    # Add assistant response to history, attributed to the producing LLM
    st.session_state[messages_key].append(assistant_message(response, provider, model))
    save_chat_history(EXPERT_ID, st.session_state[messages_key])
```

**Chat toolbox and attachments** (see `handle_user_input()` in the template):
- `st.chat_input` and the toolbox row (`render_chat_toolbox(widget_key, config, expert_id, messages_key)` in `lib/ui/chat_toolbox.py`) are rendered inside `with st.bottom:`, so the toolbox stays pinned below the input. Left to right: "Attach file" and "Attach image" (popovers with a multi-file `st.file_uploader` each), "Voice input", status captions (skipped files, attached files/images) and, right-aligned via `st.space("stretch")`, "Clear chat history" and the context usage. It returns a `ToolboxInput(attachments, images, voice_prompt)`: text files as (name, text), images as (name, bytes), plus an optional transcribed voice prompt.
- **Text files** (UTF-8, at most `ATTACHMENT_MAX_SIZE_KB` = 200 KB each, extensions from `ATTACHMENT_FILE_TYPES` in `lib/shared/constants.py`): too-large or non-UTF-8 files are reported in the toolbox and skipped. On send, `build_message_content()` (`lib/shared/attachments.py`) appends each file to the prompt as an `<attachment name="...">...</attachment>` block, so token counting, chat history persistence and size limits need no changes.
- **Images** (`IMAGE_FILE_TYPES` = PNG/JPEG/WebP/GIF, at most `IMAGE_MAX_SIZE_MB` = 5 MB each, validated with Pillow by `validate_image_attachment()`): the button is disabled, with the tooltip "<model> does not support images", unless `supports_images(provider, model)` is true, i.e. the model config in `LLM_PROVIDERS` declares `"vision": True`.
  - On send, `save_image()` (`lib/storage/attachment_store.py`) writes each image to `chat_attachments/{expert_id}/<uuid>.<ext>` (resolved from the project root, path-traversal safe via `safe_path_join`) and returns a reference. The message content only gets an `<image name="..." ref="...">` tag after the prompt (before any `<attachment>` blocks), which keeps the chat history small and the token count undistorted. Images are therefore **not** counted in the context usage.
  - When a request is sent, every message goes through `to_api_content(content, images_supported)`: image tags become OpenAI-style `image_url` parts with base64 data URLs (`get_image_data_url()`). For models without image support each image is replaced by the text note "[Image <name> omitted: the selected model does not support images]", so switching an expert to a text-only model keeps earlier conversations working; a missing file becomes "[Image <name> is no longer available]". Messages without images are passed through unchanged.
- "Voice input": `_render_voice_input()` records with `st.audio_input` and calls `lib/audio/transcription.py`. `get_transcription_provider()` routes OpenAI experts to OpenAI (`gpt-transcribe`) and all other experts to Z.AI (`glm-asr-2512`, max 30 s, checked via `get_audio_duration()` before sending); both use the OpenAI-compatible `/audio/transcriptions` endpoint through the pooled client (`get_cached_client(...).client.audio.transcriptions.create`). Without the transcription provider's API key the recorder is disabled with a notice. GLM-ASR gets the localized sentence `chat_toolbox.voice_asr_context` as `prompt` (it has no language parameter; without context it answered German in Chinese or English); OpenAI gets the app language as ISO-639-1 `language`. The transcript is sent automatically: it is returned right away as `ToolboxInput.voice_prompt`, which `handle_user_input()` treats like a typed prompt (`prompt = prompt or toolbox.voice_prompt`). Each recording is transcribed, and therefore sent, once: the result is cached in session state by audio hash, and the recorder key changes after the message was sent. `render_chat_toolbox()` returns a `ToolboxInput` dataclass (attachments, images, voice_prompt).
- "Clear chat history" lives in the toolbox (right side, left of the context usage) as a popover with a confirmation button (`_render_clear_history()` in `lib/ui/chat_toolbox.py`; the sidebar button and the template's `clear_chat_history()` were removed). `delete_chat_history()` also calls `delete_expert_attachments()`; `scripts/reset_application.py` deletes the whole `chat_attachments/` directory.
- `render_user_message()` uses `split_message_content()`, which returns `(prompt, text attachments, images)`, to show the prompt, image thumbnails (`st.image(..., width=240, alt=<file name>)`, or a "no longer available" caption) and one collapsible "📎 <filename>" expander per text attachment, also after a reload.
- **Context usage**: `_render_context_usage()` shows a compact popover button "<severity emoji> <percent>%" on the right of the toolbox; it opens the details (usage %, total/max tokens, system prompt tokens, chat message tokens), calculated by `_calculate_context_stats()` via `TokenManager.calculate_usage_statistics()`. It replaces the former sidebar metric card and breakdown expander (`display_context_usage()` in the template, removed).
- The uploader keys include a counter that is incremented after each sent message, which clears the attachments.

### Model Settings (toolbox, second row)

The former sidebar "Model settings" (model, thinking mode, temperature, provider links, save button) were replaced by a row in the toolbox, rendered by `_render_model_settings()` in `lib/ui/chat_toolbox.py` below the toolbox row:

- **Model dropdown**: options are `"provider/model"` for every provider with an API key (`_model_options()`, catalog order of `LLM_PROVIDERS`; the current model is always included). Choosing a model of another provider switches the expert's provider.
- **Thinking**: `_render_thinking_select()` shows an effort selectbox for models with `reasoning_efforts` (unsupported stored levels → model default via `resolve_reasoning_effort()`), nothing for `thinking_always_on` models, and enabled/disabled for older Z.AI models and KIMI K2.6.
- **Temperature**: a number input only if `get_fixed_temperature()` is None (DeepSeek, Z.AI).
- **Saving**: immediately via `ConfigManager.update_config()` (provider, model, thinking_level, temperature) + `invalidate_expert_cache()` + rerun — but only after a real user change, signalled by the widgets' `on_change` callback (`_mark_model_settings_changed()`), so merely displaying a normalized default never writes the config.
- **Avatars per answer**: assistant messages are created with `assistant_message(content, provider, model)` (`lib/storage/chat_history_manager.py`); the chat history persists `provider`/`model` per message, background streams store them in the stream metadata (`StreamingCache.get_llm_origin()`), and `render_chat_interface()` picks the avatar per message (fallback: current provider for older messages).

The sidebar now only contains the page navigation and the Git branch footer.

## Advantages of Template System

### 1. DRY Principle

**Before Template**: Each expert page coded separately
```python
# pages/1001_python_expert.py
# 300+ lines of expert-specific code

# pages/1002_data_scientist.py
# 300+ lines of nearly identical code
# ❌ Violates DRY principle
```

**After Template**: Single template for all experts
```python
# templates/template.py
# 300 lines of template code
# Generated to 1001_python_expert.py, 1002_data_scientist.py, etc.
# ✅ Follows DRY principle
```

### 2. Consistent UI/UX

All experts have:
- Same layout
- Same controls
- Same behavior
- Same user experience

### 3. Easy Maintenance

**Adding a feature**: Update template once, regenerate all

**Example**: Add a new button to the chat page
```bash
# 1. Add button to template (1 file)
vim templates/template.py

# 2. Regenerate all expert pages
uv run python scripts/regenerate_pages.py

# 3. Done! All experts now have the new button
```

### 4. Scalability

**Adding 100 experts**:
- Without template: Write 100 × 300 lines = 30,000 lines
- With template: Write 1 × 300 lines = 300 lines (template) + 100 configs

**Efficiency gain**: 99% reduction in code

## Limitations and Considerations

### 1. All Experts Share Same UI

**Limitation**: Cannot have expert-specific UI without template logic

**Workaround**: Use conditional logic in template based on config values

**Example**:
```python
# In template
if config.get("custom_ui"):
    # Render custom UI
else:
    # Render standard UI
```

### 2. Regeneration Overwrites Custom Edits

**Limitation**: Manual edits to generated pages are lost on regeneration

**Solution**: Never edit generated pages. Always update template instead.

### 3. Regeneration Affects All Experts

**Limitation**: Cannot regenerate individual experts

**Solution**: Test thoroughly before regenerating all

## Best Practices

### 1. Keep Expert Logic in Configs

**Good**:
```yaml
# configs/1001_python_expert.yaml
system_prompt: |
  Custom Python-specific instructions...
```

**Bad**:
```python
# In template
if EXPERT_ID == "1001_python_expert":
    # Python-specific logic
```

### 2. Use Utility Functions

**Good**:
```python
# In template
from lib.shared.helpers import translate_expert_name

st.title(f"🤖 {translate_expert_name(config.get('expert_name', EXPERT_NAME))}")
```

**Bad**:
```python
# In template - duplicate logic
if EXPERT_ID == "1001_python_expert":
    st.markdown("Welcome to Python Expert...")
elif EXPERT_ID == "1002_data_scientist":
    st.markdown("Welcome to Data Scientist...")
```

### 3. Test Before Regenerating

**Workflow**:
1. Edit template
2. Create test expert
3. Verify feature works
4. Delete test expert
5. Regenerate all experts
6. Test multiple experts

## Troubleshooting

### Template Changes Not Appearing

**Problem**: Modified template but expert pages unchanged

**Solution**:
```bash
# Regenerate expert pages
uv run python scripts/regenerate_pages.py
```

### Regeneration Failed

**Problem**: Error during regeneration

**Common Causes**:
1. Syntax error in template
2. Missing utility functions
3. Invalid placeholder names

**Solution**:
1. Check template for syntax errors
2. Verify all imports exist
3. Check placeholder names: `{{EXPERT_ID}}`, `{{EXPERT_NAME}}`

### Expert Page Not Loading

**Problem**: Navigation to expert page shows error

**Possible Cause**: Expert page out of sync with template

**Solution**:
```bash
# Regenerate all pages
uv run python scripts/regenerate_pages.py
```

## Related Documentation

- **[Architecture Overview](overview.md)** - System architecture
- **[Development - Adding Features](../development/adding-features.md)** - Feature development
- **[Configuration - Expert Configs](../configuration/expert-configs.md)** - Expert YAML configs

---

**Back to**: [Documentation Home](../README.md) | [Architecture Overview](overview.md)
