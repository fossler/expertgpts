# Expert Configuration Guide

This guide explains expert configuration files in ExpertGPTs, including YAML structure, available fields, and best practices.

## Overview

Each expert in ExpertGPTs is defined by a **YAML configuration file** stored in the `configs/` directory. These files contain all information about an expert: name, description, behavior, and metadata.

## Configuration File Structure

### Location and Naming

**Location**: `configs/` directory in project root

**Naming Convention**: `{expert_id}.yaml`

**Examples**:
- `configs/1001_python_expert.yaml`
- `configs/1002_data_scientist.yaml`
- `configs/1005_sql_expert.yaml`

**Expert ID Format**: `{number}_{sanitized_name}`
- Number: 1001-9997 (reserved: 1000=Home, 9998=Settings, 9999=Help)
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
  version: "1.0"
  model: "deepseek-chat"
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
**Required**: Yes
**Range**: 0.0 to 2.0
**Default**: 0.7

**Purpose**: Controls response creativity and randomness

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

**Auto-Generated Prompt** (if not provided):
The system generates a prompt based on the description field.

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
- `version`: Expert configuration version
- `model`: Default LLM model

**Example**:
```yaml
metadata:
  version: "1.0"
  model: "deepseek-chat"
```

**Purpose**: Stores additional expert information

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
  version: "1.0"
  model: "deepseek-chat"
```

---

### Example 2: Advisory Expert

**File**: `configs/1006_career_coach.yaml`

```yaml
expert_id: "1006_career_coach"
expert_name: "Career Coach"
description: "Career coach specializing in tech industry transitions. Provides guidance on resume building, interview preparation, salary negotiation, and career path planning for software developers."
temperature: 0.7
system_prompt: |
  You are Career Coach, a domain-specific expert AI assistant.

  ## Your Expertise
  Specializing in career guidance for software developers and tech professionals.

  You help with:
  - Resume building and optimization
  - LinkedIn profile enhancement
  - Interview preparation (technical and behavioral)
  - Salary negotiation strategies
  - Career path planning
  - Industry transitions
  - Professional networking

  ## Guidelines
  - Provide actionable, practical advice
  - Consider individual goals and circumstances
  - Encourage continuous learning and growth
  - Balance realism with optimism
  - Acknowledge when more information is needed

  ## Response Style
  - Encouraging and supportive
  - Professional but approachable
  - Practical with specific examples
  - Tailored to tech industry context
created_at: "2025-01-17T11:00:00.000000"
metadata:
  version: "1.0"
  model: "deepseek-chat"
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
  version: "1.0"
  model: "deepseek-chat"
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

**Note**: All fields except `system_prompt`, `created_at`, and `metadata` are optional with defaults.

---

## Creating Configuration Files

### Via UI (Recommended)

1. Navigate to **Home** page
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
5. Regenerate expert pages or restart app

**Example**:
```bash
cd configs/
vim 1015_custom_expert.yaml
# Add YAML content
cd ..
python3 scripts/reset_application.py
```

**Caution**:
- Must be valid YAML syntax
- Indentation matters (use spaces, not tabs)
- Expert ID must be unique
- Must use correct number range (1001-9998)

## Editing Configuration Files

### Via UI

1. Navigate to **Home** page
2. Find expert in list
3. Click **Edit**
4. Modify fields
5. Click **"Save Changes"**

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
streamlit run app.py  # Restart app
```

**Caution**:
- Validate YAML syntax before saving
- Backup file before editing
- Test changes after restart
- Invalid syntax can cause app errors

## Deleting Configuration Files

### Via UI (Recommended)

1. Navigate to **Home** page
2. Find expert in list
3. Click **Delete**
4. Confirm deletion

**Removes**:
- Configuration file: `configs/{expert_id}.yaml`
- Expert page: `pages/{expert_id}.py`
- Chat history: `chat_history/{expert_id}.json`

### Manual Deletion

**Not recommended** - Can leave orphaned files

**If manually deleting**:
```bash
# Delete config
rm configs/1001_python_expert.yaml

# Delete expert page
rm pages/1001_python_expert.py

# Delete chat history (optional)
rm chat_history/1001_python_expert.json
```

**Warning**: Irreversible. Backup important conversations first.

## Configuration Validation

### Required Field Validation

All configurations must have:
- `expert_id` (unique)
- `expert_name` (non-empty)
- `description` (non-empty)
- `temperature` (0.0-2.0)

### Type Validation

- `expert_id`: String
- `expert_name`: String
- `description`: String
- `temperature`: Float/Number
- `system_prompt`: String (optional)
- `created_at`: String (optional)
- `metadata`: Dictionary (optional)

### Range Validation

- `temperature`: Must be between 0.0 and 2.0
- `expert_id` number: 1001-9998

### Uniqueness Validation

- `expert_id` must be unique across all configs

## Configuration Best Practices

### 1. Use Version Control

**Recommended**: Commit expert configs to git

```bash
git add configs/*.yaml
git commit -m "Add SQL expert configuration"
```

**Benefits**:
- Tracks changes over time
- Enables collaboration
- Provides backup
- Documents evolution

### 2. Document Custom Prompts

Add comments to explain expert behavior:

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

Test configuration before committing:

```bash
# Test app loads without errors
streamlit run app.py

# If no errors, commit
git add configs/1001_python_expert.yaml
git commit -m "Update Python Expert temperature to 0.3"
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

**Cause**: Temperature set outside 0.0-2.0 range

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
  version: "1.0"
  model: "deepseek-chat"
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
  version: "1.0"
  model: "deepseek-chat"
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
  version: "1.0"
  model: "deepseek-chat"
```

## Next Steps

- **[Creating Experts Guide](../user-guide/creating-experts.md)** - Create experts via UI
- **[Configuration Overview](overview.md)** - Configuration system overview
- **[User Guide - Basics](../user-guide/basics.md)** - Using experts in conversations
- **[Development - Adding Features](../development/adding-features.md)** - Advanced configuration

---

**Back to**: [Documentation Home](../README.md) | [Configuration Overview](overview.md)
