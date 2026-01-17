# App Defaults Guide

This guide explains the application defaults configuration in ExpertGPTs, which controls default LLM settings and language preferences.

## Overview

The application defaults are stored in `.streamlit/app_defaults.toml` and control:
- **Default LLM provider** (DeepSeek, OpenAI, Z.AI)
- **Default model** for the selected provider
- **Default temperature** for new experts
- **Default thinking level** for reasoning
- **Language preference** for the UI

These defaults apply when:
- Creating new experts
- Starting the application for the first time
- No expert-specific override exists

## Configuration File

### Location

**File Path**: `.streamlit/app_defaults.toml`

**Git Status**: Ignored (not tracked in version control)

**Permissions**: 600 (owner read/write only)

### Example File

**Location**: `.streamlit/app_defaults.toml.example`

```toml
# ExpertGPTs Application Defaults
#
# This file stores your default LLM settings and language preference
#
# Settings are managed via the Settings page in the app
# You can also edit this file manually

[llm]
provider = "deepseek"
model = "deepseek-chat"
temperature = 0.7
thinking_level = "none"

[language]
code = "en"
```

## Configuration Sections

### LLM Settings (`[llm]`)

Controls default LLM provider and model settings.

#### `provider`

**Type**: String
**Valid Values**: `"deepseek"`, `"openai"`, `"zai"`
**Default**: `"deepseek"`

**Purpose**: Default LLM provider for new experts

**Example**:
```toml
[llm]
provider = "deepseek"
```

**Impact**:
- New experts use this provider by default
- Can be overridden per-expert
- Doesn't affect existing experts

**See also**: [API Providers Guide](../api/providers.md)

---

#### `model`

**Type**: String
**Valid Values**: Depends on provider

**DeepSeek Models**:
- `"deepseek-chat"` - Standard model (default)
- `"deepseek-reasoner"` - Reasoning-optimized model

**OpenAI Models**:
- `"o3-mini"` - Mini reasoning model (default)
- `"gpt-4o"` - Flagship model
- `"gpt-4o-mini"` - Cost-effective option

**Z.AI Models**:
- `"glm-4.7"` - Standard model (default)
- `"glm-4.7-thinking"` - Reasoning-enabled model

**Example**:
```toml
[llm]
provider = "openai"
model = "gpt-4o"
```

**Impact**:
- New experts use this model by default
- Model must be available for selected provider
- Can be overridden per-expert

---

#### `temperature`

**Type**: Float
**Range**: 0.0 to 2.0
**Default**: 0.7

**Purpose**: Default temperature for new experts

**Quick Reference**:
- **0.0 - 0.3**: Focused, deterministic (coding, math)
- **0.4 - 0.7**: Balanced, informative (general advice)
- **0.8 - 1.2**: Creative, exploratory (brainstorming)
- **1.3 - 2.0**: Highly creative (creative writing)

**Example**:
```toml
[llm]
temperature = 0.5
```

**Impact**:
- New experts created with this temperature
- Can be adjusted per-expert
- Doesn't affect existing experts

**See also**: [Temperature Guide](../user-guide/temperature-guide.md)

---

#### `thinking_level`

**Type**: String
**Valid Values**: `"none"`, `"low"`, `"medium"`, `"high"`
**Default**: `"none"`

**Purpose**: Enable/disable reasoning capabilities by default

**Availability**:
- **OpenAI**: All levels supported
- **DeepSeek**: Enabled/disabled based on model selection
- **Z.AI**: Enabled/disabled via extra_body parameter

**Example**:
```toml
[llm]
thinking_level = "medium"
```

**Impact**:
- New experts use this thinking level
- Increases response time and cost when enabled
- Use for complex problem-solving tasks

**Use Cases**:
- **None**: Quick responses, simple tasks
- **Low**: Light reasoning, moderate complexity
- **Medium**: Balanced reasoning for complex tasks
- **High**: Deep reasoning for challenging problems

---

### Language Settings (`[language]`)

Controls UI language and expert response language.

#### `code`

**Type**: String (language code)
**Valid Values**: See supported languages below
**Default**: Auto-detected on first run

**Purpose**: UI and response language preference

**Supported Languages**:

| Language | Code | Script Family |
|----------|------|---------------|
| English | `en` | Latin |
| German | `de` | Latin |
| Spanish | `es` | Latin |
| French | `fr` | Latin |
| Italian | `it` | Latin |
| Portuguese | `pt` | Latin |
| Russian | `ru` | Cyrillic |
| Turkish | `tr` | Latin |
| Indonesian | `id` | Latin |
| Malay | `ms` | Latin |
| Chinese (Simplified) | `zh-CN` | Han (汉字) |
| Chinese (Traditional) | `zh-TW` | Han (漢字) |
| Classical Chinese | `wyw` | Han (文言) |
| Cantonese | `yue` | Han (粵語) |

**Example**:
```toml
[language]
code = "de"  # German
```

**Behavior**:
- **First Run**: System language auto-detected and saved
- **Manual Change**: Updated via Settings page
- **Persistence**: Saved for future app runs
- **Expert Responses**: Experts automatically respond in this language

**See also**: [Internationalization Guide](../internationalization/I18N_GUIDE.md)

---

## Configuration Lifecycle

### First Run

1. **Language Detection**:
   - App detects system language automatically
   - Saves to `app_defaults.toml`
   - App starts in detected language

2. **Default Provider**:
   - Defaults to DeepSeek if not configured
   - Can be changed via Settings page

### Subsequent Runs

1. **Load Preferences**:
   - Read from `app_defaults.toml`
   - Apply to all new experts
   - UI starts in saved language

2. **Updates**:
   - Changed via Settings page
   - Saved immediately
   - Applied to next expert created

### Resetting Defaults

**Option 1: Delete File** (app will recreate with defaults)
```bash
rm .streamlit/app_defaults.toml
# App will recreate on next run with auto-detected language
```

**Option 2: Reset via Settings Page** (if available)
- Navigate to Settings → General
- Reset to defaults button

**Option 3: Manual Edit**
```bash
vim .streamlit/app_defaults.toml
# Edit values
# Save and restart app
```

## Managing Defaults

### Via Settings Page (Recommended)

1. Navigate to **Settings** → **General** tab
2. Find the setting you want to change
3. Use dropdown/slider to adjust
4. Click outside the control to save
5. Settings saved immediately to `app_defaults.toml`

**Benefits**:
- Automatic validation
- Immediate persistence
- No syntax errors
- User-friendly interface

### Manual Configuration

For advanced users or automated setup.

**Steps**:

1. **Open file**:
   ```bash
   vim .streamlit/app_defaults.toml
   ```

2. **Edit values**:
   ```toml
   [llm]
   provider = "openai"
   model = "gpt-4o"
   temperature = 0.5
   thinking_level = "medium"

   [language]
   code = "de"
   ```

3. **Save and restart app**:
   ```bash
   streamlit run app.py
   ```

**Caution**:
- Must be valid TOML syntax
- Invalid values cause app errors
- Backup file before editing
- Use Settings page when possible

## Configuration Examples

### Example 1: Cost-Effective Setup

**Use Case**: Daily use, cost-conscious

```toml
[llm]
provider = "deepseek"
model = "deepseek-chat"
temperature = 0.7
thinking_level = "none"

[language]
code = "en"
```

**Rationale**:
- DeepSeek: Most cost-effective provider
- deepseek-chat: Standard model, good quality
- Temperature 0.7: Balanced for most use cases
- No reasoning: Faster responses

---

### Example 2: Quality-Focused Setup

**Use Case**: Complex problem-solving, quality priority

```toml
[llm]
provider = "openai"
model = "o3-mini"
temperature = 0.5
thinking_level = "medium"

[language]
code = "en"
```

**Rationale**:
- OpenAI: Advanced reasoning capabilities
- o3-mini: Optimized for reasoning tasks
- Temperature 0.5: Focused but flexible
- Medium thinking: Balanced reasoning

---

### Example 3: Multilingual Setup

**Use Case**: Chinese language optimization

```toml
[llm]
provider = "zai"
model = "glm-4.7"
temperature = 0.7
thinking_level = "none"

[language]
code = "zh-CN"
```

**Rationale**:
- Z.AI: GLM models optimized for Chinese
- Simplified Chinese: Primary language
- Temperature 0.7: Balanced responses
- No reasoning: Faster responses

---

### Example 4: Development Setup

**Use Case**: Development and testing

```toml
[llm]
provider = "deepseek"
model = "deepseek-chat"
temperature = 0.3
thinking_level = "none"

[language]
code = "en"
```

**Rationale**:
- Low temperature: Consistent, predictable responses
- DeepSeek: Cost-effective for testing
- No reasoning: Faster iterations
- English: Universal development language

---

## Defaults vs. Expert-Specific Settings

### Understanding Precedence

**Priority Order**:
1. **Session State** (current session override)
2. **Expert Config** (per-expert setting)
3. **App Defaults** (global default)
4. **Application Defaults** (hardcoded fallback)

**Example**: Temperature setting
```
User changes temperature in current session → 0.8
    ↓
Expert config has temperature → 0.6
    ↓
App defaults temperature → 0.7
    ↓
Application fallback → 0.7
```

**Result**: Session state wins (0.8)

### When Defaults Apply

**Defaults apply to**:
- ✅ New experts created after setting defaults
- ✅ Experts without explicit settings
- ✅ Application initialization

**Defaults don't apply to**:
- ❌ Existing experts (they keep their settings)
- ❌ Session state overrides
- ❌ Expert-specific configuration

**Example Workflow**:
```toml
# Initial: App defaults temperature = 0.7

# Create Expert A → Uses 0.7
# Create Expert B → Uses 0.7

# Change app defaults to 0.5

# Create Expert C → Uses 0.5 (new default)
# Expert A → Still uses 0.7 (existing)
# Expert B → Still uses 0.7 (existing)

# Edit Expert A to temperature 0.3

# Expert A → Uses 0.3 (expert-specific)
# App defaults → Still 0.7
```

## Best Practices

### 1. Set Defaults Before Creating Experts

**Recommended Workflow**:
1. Configure app defaults first
2. Create experts (they inherit defaults)
3. Adjust individual experts as needed

**Rationale**: Easier than updating multiple experts later

### 2. Choose Appropriate Defaults

**Consider Your Use Case**:
- **Personal use**: Your preferred provider/model
- **Team use**: Most common requirements
- **Development**: Cost-effective, fast responses
- **Production**: Quality-focused, reliable

### 3. Balance Cost and Quality

**Cost-Effective**:
```toml
provider = "deepseek"
thinking_level = "none"
```

**Quality-Focused**:
```toml
provider = "openai"
thinking_level = "medium"
```

**Balanced**:
```toml
provider = "deepseek"
thinking_level = "none"
# Use OpenAI selectively per-expert for complex tasks
```

### 4. Use Temperature Wisely

**Default Temperature**:
- **0.7** for general use (recommended)
- **0.3-0.5** for technical/development work
- **0.8-1.0** for creative/advisory work

### 5. Set Language Once

**Recommended**: Set language on first run, let it persist

**Not Recommended**: Frequently changing language
- Experts adapt via language prefix injection
- No need to change language per expert
- UI updates immediately

## Troubleshooting

### Defaults Not Applying

**Problem**: Created expert but it doesn't use app defaults

**Explanation**: Defaults only apply to new experts

**Solutions**:
1. Set defaults before creating experts
2. Or manually edit existing experts
3. Or edit expert configs directly

### Language Not Changing

**Problem**: Changed language but UI still in English

**Solutions**:
1. App restarts automatically - wait for reload
2. Check browser cache (clear and reload)
3. Verify `app_defaults.toml` was updated
4. Try selecting language again

### Invalid Provider/Model

**Problem**: Set provider/model but getting errors

**Cause**: Invalid combination

**Example**:
```toml
# INVALID
provider = "deepseek"
model = "gpt-4o"  # Wrong! gpt-4o is OpenAI
```

**Solution**: Match provider with correct model:
```toml
# VALID
provider = "openai"
model = "gpt-4o"  # Correct!
```

### File Permission Errors

**Problem**: Can't save `app_defaults.toml`

**Solution**:
```bash
# Check directory permissions
ls -la .streamlit/

# Fix if needed
chmod 755 .streamlit/
chmod 600 .streamlit/app_defaults.toml
```

## File Reference

### Complete Example

```toml
# ExpertGPTs Application Defaults
#
# This file stores your default LLM settings and language preference

[llm]
# Default LLM provider: "deepseek", "openai", or "zai"
provider = "deepseek"

# Default model for the provider
# DeepSeek: "deepseek-chat", "deepseek-reasoner"
# OpenAI: "o3-mini", "gpt-4o", "gpt-4o-mini"
# Z.AI: "glm-4.7", "glm-4.7-thinking"
model = "deepseek-chat"

# Default temperature for new experts (0.0 - 2.0)
temperature = 0.7

# Default thinking level: "none", "low", "medium", "high"
thinking_level = "none"

[language]
# Language code for UI and expert responses
# Supported: en, de, es, fr, it, pt, ru, tr, id, ms, zh-CN, zh-TW, wyw, yue
code = "en"
```

## Next Steps

- **[Configuration Overview](overview.md)** - Configuration system overview
- **[User Guide - Customization](../user-guide/customization.md)** - Settings page usage
- **[API Providers Guide](../api/providers.md)** - Provider-specific details

---

**Back to**: [Documentation Home](../README.md) | [Configuration Overview](overview.md)
