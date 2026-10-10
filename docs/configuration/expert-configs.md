# Expert Configuration Guide

This guide explains expert configuration files in ExpertGPTs, including YAML structure, available fields, and best practices.

## Overview

Each expert in ExpertGPTs is defined by a **YAML configuration file** stored in the `configs/` directory. These files contain all information about an expert: name, description, behavior, and metadata.

## Configuration File Structure

### Location and Naming

**Location**: `configs/` directory in project root

**Naming Convention**: `{expert_id}.yaml`

**Examples**:
- `configs/1001_helpful_assistant.yaml`
- `configs/1007_data_scientist.yaml`
- `configs/1011_sql_expert.yaml`

**Expert ID Format**: `{number}_{sanitized_name}`
- Number: next free number from 1001 upward (highest existing expert page + 1; reserved: 1000=Home, 9998=Settings, 9999=Help)
- Sanitized name: Lowercase, spaces/hyphens to underscores

### Example Configuration

```yaml
expert_id: "1001_python_expert"
expert_name: "Python Expert"
description: "Expert in Python programming, software development, debugging, and best practices"
temperature: 0.7
system_prompt: |
  You are Python Expert, a domain-specific expert AI assistant.

  ## Your Expertise
  Expert in Python programming, software development, debugging, and best practices...

  ## Guidelines
  - Provide accurate, expert-level information in your domain
  - If you're unsure about something, acknowledge it honestly
  - Use clear, professional language appropriate for your domain
created_at: "2025-01-17T12:00:00.123456"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "high"
```

## Configuration Fields

### Required Fields

#### `expert_id`

**Type**: String
**Required**: Yes
**Unique**: Yes

**Format**: `{number}_{sanitized_name}`

**Examples**:
- `"1001_python_expert"`
- `"1002_data_scientist"`
- `"1005_career_coach"`

**Constraints**:
- Must be unique across all experts
- Must start with number (1001-9997)
- Cannot use 1000 (Home), 9998 (Settings), or 9999 (Help)
- Sanitized: lowercase, underscores only

**Auto-Generated**: Created automatically when expert is added via UI

---

#### `expert_name`

**Type**: String
**Required**: Yes
**Min Length**: 1 character
**Max Length**: No hard limit (practical: 50 characters)

**Purpose**: Human-readable name for the expert

**Examples**:
- `"Python Expert"`
- `"Data Scientist"`
- `"Legal Advisor"`
- `"Datenexperte"` (German)

**Guidelines**:
- Use descriptive, clear names
- Can be in any language
- Avoid special characters
- Keep concise but informative

**Display**: Shown in navigation menu and expert page header

---

#### `description`

**Type**: String
**Required**: Yes
**Multi-line**: Yes
**Min Length**: 1 character

**Purpose**: Describes the expert's domain and capabilities

**Examples**:

✅ **Good**:
```yaml
description: "Expert in SQL database design, query optimization, and database administration. Specializes in PostgreSQL, MySQL, and SQLite. Helps with schema design, complex queries, performance tuning, and database best practices."
```

✅ **Good**:
```yaml
description: |
  Career coach specializing in tech industry transitions. Provides guidance on:
  - Resume building and optimization
  - Interview preparation (technical and behavioral)
  - Salary negotiation strategies
  - Career path planning for software developers
```

❌ **Too vague**:
```yaml
description: "An expert that helps with stuff."
```

**Purpose**:
- Shown on expert page
- Used for auto-generating system prompt (if no custom prompt)
- Helps users understand expert capabilities

---

#### `temperature`

**Type**: Float
**Required**: No (falls back to `1.0`)
**Range**: 0.0 to 2.0 (Z.AI: 0.0 to 1.0, `max_temperature`)
**Default**: 1.0

**Purpose**: Controls response creativity and randomness

**Limits**: Some models ignore the stored value and use a fixed temperature (`fixed_temperature`): all OpenAI models `1.0`; KIMI `kimi-k3` / `kimi-k2.7-code*` `1.0`; `kimi-k2.6` `1.0` with thinking, `0.6` without. DeepSeek ignores temperature while thinking is enabled. Change it in the chat toolbox on the expert page (saved immediately) or in the edit dialog.

**Quick Reference**:
- **0.0 - 0.3**: Focused, deterministic (coding, math)
- **0.4 - 0.7**: Balanced, informative (general advice)
- **0.8 - 1.2**: Creative, exploratory (brainstorming)
- **1.3 - 2.0**: Highly creative (creative writing)

**Examples**:
```yaml
# Code expert - focused
temperature: 0.3

# General advisor - balanced
temperature: 0.7

# Creative writer - creative
temperature: 1.2
```

**See also**: [Temperature Guide](../user-guide/temperature-guide.md)

---

### Optional Fields

#### `system_prompt`

**Type**: String
**Required**: No (auto-generated if not provided)
**Multi-line**: Yes

**Purpose**: Custom instructions for expert behavior

**When to Use**:
- You need precise control over expert behavior
- Auto-generated prompt doesn't meet requirements
- Expert requires specific formatting or constraints
- Expert needs disclaimers (legal, medical, financial)

**Format**: Use `|` for multi-line prompts

**Examples**:

**Code Review Expert**:
```yaml
system_prompt: |
  You are a Code Review Expert specializing in Python.

  Your role:
  - Review code for bugs, security issues, and best practices
  - Suggest improvements for readability and performance
  - Follow PEP 8 style guidelines
  - Provide specific, actionable feedback

  Your responses should:
  - Start with a summary of findings
  - List issues by severity (critical, major, minor)
  - Provide code examples for improvements
  - Be constructive and educational

  If you're unsure about something, acknowledge it honestly.
```

**Legal Expert with Disclaimers**:
```yaml
system_prompt: |
  You are a Legal Information Expert specializing in contract law.

  Your role:
  - Explain legal concepts in plain language
  - Identify common clauses and their implications
  - Highlight potential risks in contracts

  Important constraints:
  - You provide information, not legal advice
  - Always recommend consulting a qualified attorney
  - Do not interpret specific documents for real-world use
  - Cite general legal principles when applicable

  Your responses should be clear, accurate, and include appropriate disclaimers.
```

**Auto-Generated Prompt** (if left empty in the UI):
The system generates a prompt based on the description field (AI-generated with the selected provider, or a template fallback). A manually created YAML file without `system_prompt` gets no generated prompt.

---

#### `created_at`

**Type**: String (ISO 8601 timestamp)
**Required**: No (auto-generated)
**Format**: `"YYYY-MM-DDTHH:MM:SS.ffffff"`

**Example**:
```yaml
created_at: "2025-01-17T12:00:00.123456"
```

**Purpose**: Tracks when expert was created

**Auto-Generated**: Set automatically when expert is created

---

#### `metadata`

**Type**: Dictionary (key-value pairs)
**Required**: No

**Common Fields**:
- `version`: Expert configuration version (`"2.0"` for new experts)
- `provider`: LLM provider (`deepseek`, `openai`, `zai`, `kimi`; fallback `deepseek`)
- `model`: LLM model of that provider (fallback: the provider's default model)
- `thinking_level`: Thinking/reasoning level (e.g. `none`, `low`, `medium`, `high`, `xhigh`, `max`; fallback `none`; unsupported levels fall back to the model's default)

**Example**:
```yaml
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "high"
```

**Purpose**: Stores the expert's LLM settings (read by `get_llm_metadata()` in `lib/config/config_manager.py`)

**Updated by**: the model, thinking and temperature controls in the chat toolbox (`lib/ui/chat_toolbox.py`), which save `provider`, `model`, `thinking_level` and `temperature` to `configs/{expert_id}.yaml` immediately, and by the edit dialog. Updates also set an `updated_at` timestamp.

**Extensibility**: Can add custom fields as needed

---

## Complete Configuration Examples

### Example 1: Technical Expert

**File**: `configs/1001_python_expert.yaml`

```yaml
expert_id: "1001_python_expert"
expert_name: "Python Expert"
description: "Expert in Python programming, software development, debugging, and best practices. Specializes in Flask, FastAPI, data science libraries, and Python ecosystem."
temperature: 0.3
system_prompt: |
  You are Python Expert, a domain-specific expert AI assistant.

  ## Your Expertise
  Expert in Python programming, software development, debugging, and best practices.

  You specialize in:
  - Core Python (syntax, data structures, algorithms)
  - Web frameworks (Flask, FastAPI, Django)
  - Data science (NumPy, Pandas, Matplotlib)
  - Testing (pytest, unittest)
  - Best practices and PEP 8 style guidelines

  ## Guidelines
  - Provide accurate, expert-level information
  - Show code examples with explanations
  - Follow PEP 8 style guidelines
  - Suggest best practices and common pitfalls
  - If unsure, acknowledge it honestly

  ## Response Style
  - Clear, concise, and technical
  - Code examples with comments
  - Practical, real-world applications
created_at: "2025-01-17T10:00:00.000000"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

---

### Example 2: General-Purpose Expert

**File**: `configs/1001_helpful_assistant.yaml`

```yaml
expert_id: "1001_helpful_assistant"
expert_name: "Helpful Assistant"
description: "As an AI, I embrace the role of a helpful generalist assistant, designed to provide accurate, safe, and broadly useful information across a wide range of topics and tasks."
temperature: 1.0
system_prompt: |
  # System Prompt: Helpful Assistant

  ## Identity & Purpose
  You are **Helpful Assistant**, a domain-specific AI designed to function as a knowledgeable, reliable, and supportive generalist assistant.
created_at: "2026-01-24T23:07:42.584965"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "high"
```

---

### Example 3: Creative Expert

**File**: `configs/1008_storyteller.yaml`

```yaml
expert_id: "1008_storyteller"
expert_name: "Storyteller"
description: "Creative writing assistant specializing in short fiction. Expert in narrative structure, character development, dialogue, and literary techniques."
temperature: 1.3
system_prompt: |
  You are Storyteller, a creative writing assistant specializing in short fiction.

  ## Your Expertise
  Expert in fiction writing and storytelling techniques.

  You specialize in:
  - Narrative structure and pacing
  - Character development and arcs
  - Dialogue writing and subtext
  - Literary devices (show don't tell, foreshadowing, etc.)
  - Genre conventions and innovations
  - Style and voice

  ## Guidelines
  - Encourage creativity and experimentation
  - Provide constructive feedback
  - Offer multiple approaches when appropriate
  - Balance encouragement with honest critique
  - Suggest exercises to develop skills

  ## Response Style
  - Imaginative and inspiring
  - Specific with examples
  - Respectful of author's voice
  - Open to diverse styles and genres
created_at: "2025-01-17T12:00:00.000000"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

---

### Example 4: Minimal Configuration

**File**: `configs/1010_generalist.yaml`

```yaml
expert_id: "1010_generalist"
expert_name: "General Assistant"
description: "Helpful assistant for general questions and tasks."
temperature: 0.7
```

**Note**: `system_prompt`, `created_at` and `metadata` are optional. Without `metadata`, the expert uses `deepseek` with its default model (`deepseek-flash`) and thinking level `none`; without `temperature`, `1.0` is used.

---

## Creating Configuration Files

### Via UI (Recommended)

1. Navigate to **Home** page (or Settings → Expert Management)
2. Click **"➕ Add Chat"**
3. Fill in the form
4. Click **"Create Expert"**
5. Configuration file created automatically

**Benefits**:
- Automatic validation
- No YAML syntax errors
- Proper file naming
- Auto-generated fields (expert_id, created_at)

### Manual Creation

**For advanced users**:

1. Create YAML file in `configs/` directory
2. Follow naming convention: `{number}_{sanitized_name}.yaml`
3. Add required fields
4. Save file
5. Create the matching expert page: copy any existing expert page to `pages/{expert_id}.py`, set `EXPERT_ID` and `EXPERT_NAME` in it, then run `scripts/regenerate_pages.py` to rewrite it from the template

**Example**:
```bash
cd configs/
vim 1015_custom_expert.yaml
# Add YAML content
cd ..
cp pages/1001_helpful_assistant.py pages/1015_custom_expert.py
# Set EXPERT_ID = "1015_custom_expert" and EXPERT_NAME = "Custom Expert"
uv run python scripts/regenerate_pages.py
```

Do not use `reset_application.py` here: it deletes all configs, including the new one.

**Caution**:
- Must be valid YAML syntax
- Indentation matters (use spaces, not tabs)
- Expert ID must be unique
- Use a number of 1001 or higher that no other expert uses (1000, 9998 and 9999 are reserved)

## Editing Configuration Files

### Via UI

1. Navigate to **Settings** → **Expert Management**
2. Find expert in list
3. Click **Edit**
4. Modify fields
5. Click **"Save Changes"**

Model, thinking level and temperature can also be changed directly in the chat toolbox below the chat input on the expert page; changes are saved immediately.

**Benefits**:
- Automatic validation
- Immediate effect
- No syntax errors

### Manual Editing

1. Open YAML file in text editor
2. Modify fields
3. Save file
4. Restart app or increment cache version

**Example**:
```bash
vim configs/1001_python_expert.yaml
# Edit temperature: 0.7 → 0.3
# Save and exit
uv run streamlit run app.py  # Restart app
```

**Caution**:
- Validate YAML syntax before saving
- Backup file before editing
- Test changes after restart
- Invalid syntax can cause app errors

## Deleting Configuration Files

### Via UI (Recommended)

1. Navigate to **Settings** → **Expert Management**
2. Find expert in list
3. Click **Delete**
4. Confirm deletion

**Removes**:
- Configuration file: `configs/{expert_id}.yaml`
- Expert page: `pages/{expert_id}.py`
- Chat history: `chat_history/{expert_id}.json`
- Attached images: `chat_attachments/{expert_id}/`
- A leftover streaming cache: `streaming_cache/{expert_id}_latest.*`

### Manual Deletion

**Not recommended** - Can leave orphaned files

**If manually deleting**:
```bash
# Delete config
rm configs/1001_python_expert.yaml

# Delete expert page
rm pages/1001_python_expert.py

# Delete chat history and attached images (optional)
rm chat_history/1001_python_expert.json
rm -r chat_attachments/1001_python_expert/
```

**Warning**: Irreversible. Backup important conversations first.

## Configuration Validation

### Required Field Validation

All configurations must have:
- `expert_id` (unique)
- `expert_name` (non-empty)
- `description` (non-empty)

`temperature` (0.0-2.0) is optional and defaults to `1.0`.

### Type Validation

- `expert_id`: String
- `expert_name`: String
- `description`: String
- `temperature`: Float/Number
- `system_prompt`: String (optional)
- `created_at`: String (optional)
- `metadata`: Dictionary (optional)

### Range Validation

- `temperature`: Must be between 0.0 and 2.0 (Z.AI: at most 1.0)
- `expert_id` number: 1001 or higher (1000, 9998, 9999 reserved)

### Uniqueness Validation

- `expert_id` must be unique across all configs

## Configuration Best Practices

### 1. Use Version Control

`configs/` is gitignored in the ExpertGPTs repository. To version your experts, keep them in a separate (private) repository, or download them via Settings → Danger Zone (ZIP backup).

**Benefits**:
- Tracks changes over time
- Enables collaboration
- Provides backup
- Documents evolution

### 2. Document Custom Prompts

Add comments to explain expert behavior (note: the app rewrites the file without comments when it saves changes, e.g. from the chat toolbox):

```yaml
expert_id: "1005_code_reviewer"
expert_name: "Code Reviewer"
description: "Expert in Python code review..."
# Temperature 0.3 for focused, accurate feedback
temperature: 0.3
system_prompt: |
  # Custom prompt emphasizing security and performance
  You are a Code Review Expert...
```

### 3. Use Semantic Expert IDs

**Good**:
- `1005_sql_expert`
- `1010_career_coach`
- `1015_legal_advisor`

**Less Clear**:
- `1005_expert1`
- `1010_my_expert`
- `1015_test`

### 4. Maintain Consistent Structure

Keep similar structure across expert configs:
- Order fields consistently
- Use similar prompt structure
- Standardize metadata fields

### 5. Validate Before Committing

Test configuration before committing it to your own repository:

```bash
# Test app loads without errors
uv run streamlit run app.py
```

## Troubleshooting

### Expert Not Loading

**Problem**: Expert page shows "Configuration not found"

**Solutions**:
1. Verify config file exists: `ls configs/`
2. Check filename matches expert ID
3. Validate YAML syntax
4. Check for required fields

### YAML Syntax Errors

**Problem**: Application won't start, shows YAML errors

**Common Issues**:
- Incorrect indentation (use spaces, not tabs)
- Missing quotes around strings
- Unescaped special characters
- Invalid boolean values (true/false, not True/False)

**Solution**:
1. Use YAML validator (online tools)
2. Compare with working examples
3. Check indentation consistency
4. Quote strings with special characters

### Temperature Out of Range

**Problem**: Expert not responding as expected

**Cause**: Temperature set outside the 0.0-2.0 range (Z.AI clamps values above 1.0 to 1.0)

**Solution**:
```yaml
# Incorrect
temperature: 3.0

# Correct
temperature: 1.5
```

### Duplicate Expert IDs

**Problem**: Conflicts between experts

**Cause**: Two configs with same expert_id

**Solution**:
1. Check for duplicates: `ls configs/ | grep 1001`
2. Rename one config with unique ID
3. Update corresponding expert page

## Configuration Templates

### Technical Expert Template

```yaml
expert_id: "XXXX_<name>"
expert_name: "<Technical Name>"
description: "Expert in <domain>. Specializes in <areas>."
temperature: 0.3
system_prompt: |
  You are <Expert Name>, a domain-specific expert AI assistant.

  ## Your Expertise
  Expert in <domain>...

  ## Guidelines
  - Provide accurate, technical information
  - Show code examples when applicable
  - Follow best practices
  - Acknowledge uncertainty when appropriate
created_at: "YYYY-MM-DDTHH:MM:SS.ffffff"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

### Advisory Expert Template

```yaml
expert_id: "XXXX_<name>"
expert_name: "<Advisory Name>"
description: "<Advisory role> specializing in <domain>."
temperature: 0.7
system_prompt: |
  You are <Expert Name>, a domain-specific expert AI assistant.

  ## Your Expertise
  Specializing in <domain>...

  ## Guidelines
  - Provide practical, actionable advice
  - Consider individual circumstances
  - Balance encouragement with honesty
  - Suggest resources for further learning

  ## Response Style
  - Professional but approachable
  - Supportive and constructive
  - Tailored to individual needs
created_at: "YYYY-MM-DDTHH:MM:SS.ffffff"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

### Creative Expert Template

```yaml
expert_id: "XXXX_<name>"
expert_name: "<Creative Name>"
description: "Creative assistant specializing in <creative domain>."
temperature: 1.3
system_prompt: |
  You are <Expert Name>, a creative AI assistant.

  ## Your Expertise
  Expert in <creative domain>...

  ## Guidelines
  - Encourage creativity and experimentation
  - Offer diverse perspectives
  - Provide constructive feedback
  - Inspire and motivate

  ## Response Style
  - Imaginative and inspiring
  - Respectful of creative vision
  - Open to diverse approaches
created_at: "YYYY-MM-DDTHH:MM:SS.ffffff"
metadata:
  version: "2.0"
  provider: "deepseek"
  model: "deepseek-flash"
  thinking_level: "none"
```

## Next Steps

- **[Creating Experts Guide](../user-guide/creating-experts.md)** - Create experts via UI
- **[Configuration Overview](overview.md)** - Configuration system overview
- **[User Guide - Basics](../user-guide/basics.md)** - Using experts in conversations
- **[Development - Adding Features](../development/adding-features.md)** - Advanced configuration

---

**Back to**: [Documentation Home](../README.md) | [Configuration Overview](overview.md)
