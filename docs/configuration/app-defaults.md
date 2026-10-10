# App Defaults Guide

This guide explains the application defaults configuration in ExpertGPTs, which controls default LLM settings, language preference and display settings.

## Overview

The application defaults are stored in `.streamlit/app_defaults.toml` and control:
- **Default LLM provider** (DeepSeek, OpenAI, Z.AI, KIMI)
- **Default model** for the selected provider
- **Default thinking level** for reasoning
- **Language preference** for the UI
- **Display settings** (Git branch in the sidebar footer)

These defaults apply when:
- Creating new experts (provider and model are preselected in the "Add Chat" dialog)
- Starting the application for the first time

Existing experts keep their own provider, model, thinking level and temperature in `configs/{expert_id}.yaml` (changed via the chat toolbox on the expert page).

## Configuration File

### Location

**File Path**: `.streamlit/app_defaults.toml`

**Git Status**: Ignored (not tracked in version control)

**Permissions**: 600 (owner read/write only)

### Example File

**Location**: `.streamlit/app_defaults.toml.example`

```toml
[llm]
provider = "deepseek"
model = "deepseek-flash"
thinking_level = "high"

[language]
code = "en"

[display]
git_branch = true
```

(Comments omitted; see [File Reference](#file-reference) for the full file.)

## Configuration Sections

### LLM Settings (`[llm]`)

Controls default LLM provider and model settings.

#### `provider`

**Type**: String
**Valid Values**: `"deepseek"`, `"openai"`, `"zai"`, `"kimi"`
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
- `"deepseek-flash"` - Cost-effective, 1M context, dual thinking modes (default)
- `"deepseek-v4-pro"` - Premium flagship, 1M context, dual thinking modes

**OpenAI Models**:
- `"gpt-6.1-sol"` - GPT-6.1 Sol, 1.05M context, always reasons (default)
- `"gpt-6-astra"` - GPT-6 Astra, top tier, 1.05M context, always reasons
- `"gpt-6-luna"` - GPT-6 Luna, cost-effective, 1.05M context
- `"gpt-5.6-sol"` - Frontier flagship, 1.05M context
- `"gpt-5.6-terra"` - Balanced performance/price, 1.05M context
- `"gpt-5.6-luna"` - Efficient, high-volume, 1.05M context
- `"gpt-5.4-mini"` - Cost-effective option, 400K context
- `"gpt-5.4-nano"` - High-throughput option, 400K context

**Z.AI Models**:
- `"glm-5.3"` - Flagship model, 1M context, always reasons, adjustable reasoning effort low/high/max (default)
- `"glm-5.2"` - 1M context, adjustable reasoning effort high/max
- `"glm-5"` - 200K context
- `"glm-4.7-flash"` - Free model, 200K context

**KIMI Models**:
- `"kimi-k3"` - Flagship, 1M context, always reasons, effort low/high/max (default)
- `"kimi-k2.7-code"` - Coding model, 256K context, always thinks
- `"kimi-k2.7-code-highspeed"` - Faster K2.7 Code variant, 256K context, always thinks
- `"kimi-k2.6"` - 256K context, enabled/disabled thinking

**Example**:
```toml
[llm]
provider = "openai"
model = "gpt-6.1-sol"
```

**Impact**:
- New experts use this model by default
- Model must be available for selected provider
- Can be overridden per-expert

---

#### Temperature (not an app default)

There is **no** `temperature` key in `app_defaults.toml` (the app ignores it). Temperature is stored per expert in `configs/{expert_id}.yaml`; the "Add Chat" dialog starts at `1.0`, and it can be changed later in the chat toolbox.

**Limits** (from `LLM_PROVIDERS` in `lib/shared/constants.py`):
- Range `0.0`–`2.0` by default; Z.AI caps it at `1.0` (`max_temperature`)
- Fixed values override the stored temperature (`fixed_temperature`): all OpenAI models use `1.0`; KIMI `kimi-k3` and `kimi-k2.7-code*` use `1.0`; `kimi-k2.6` uses `1.0` with thinking and `0.6` without
- DeepSeek ignores temperature while thinking is enabled (`temperature_ignored_with_thinking`), so the control is disabled then

**See also**: [Temperature Guide](../user-guide/temperature-guide.md)

---

#### `thinking_level`

**Type**: String
**Valid Values**: Model-dependent: `"none"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"`
**Default**: `"high"` in `app_defaults.toml.example`; `"none"` if the key is missing or the file is auto-created

**Purpose**: Default reasoning level, saved with the other defaults in Settings → Default LLM

**Availability**:
- **OpenAI**: `gpt-6.1-sol` / `gpt-6-astra`: low/medium/high/xhigh (always reason, default medium); other models: none/low/medium/high/xhigh (default none)
- **DeepSeek**: none/high/max (default high) for both models
- **Z.AI**: GLM-5.3: low/high/max (default max); GLM-5.2: high/max; GLM-5 / GLM-4.7-Flash: enabled/disabled
- **KIMI**: K3: low/high/max (default max); K2.7 Code: always on; K2.6: enabled/disabled

If the saved level isn't supported by the selected model, the model's default effort is used instead.

**Example**:
```toml
[llm]
thinking_level = "medium"
```

**Impact**:
- Preselected in Settings → Default LLM
- New experts currently start at `"none"` in the "Add Chat" dialog (or the model's default effort if the model doesn't support `"none"`), not at this value
- Thinking increases response time and cost when enabled

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

### Display Settings (`[display]`)

#### `git_branch`

**Type**: Boolean
**Default**: `true`

**Purpose**: Show the current Git branch in the sidebar footer. Set to `false` to hide it.

```toml
[display]
git_branch = false
```

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
   - Provider/model preselected for new experts
   - UI starts in saved language

2. **Updates**:
   - Changed via Settings page
   - LLM defaults saved with "Save Defaults"; language saved on click
   - Applied to next expert created

### Resetting Defaults

**Option 1: Delete File** (app will recreate with defaults)
```bash
rm .streamlit/app_defaults.toml
# App will recreate on next run with auto-detected language
```

**Option 2: Manual Edit**
```bash
vim .streamlit/app_defaults.toml
# Edit values
# Save and restart app
```

## Managing Defaults

### Via Settings Page (Recommended)

1. **LLM defaults**: **Settings** → **Default LLM** tab. Pick provider (only providers with an API key are listed), model and thinking mode, then click **"Save Defaults"**
2. **Language**: **Settings** → **General** tab. Click a language button; it is saved immediately and the app reloads
3. All settings are written to `app_defaults.toml`

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
   model = "gpt-6.1-sol"
   thinking_level = "medium"

   [language]
   code = "de"
   ```

3. **Save and restart app**:
   ```bash
   uv run streamlit run app.py
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
model = "deepseek-flash"
thinking_level = "none"

[language]
code = "en"
```

**Rationale**:
- DeepSeek: Most cost-effective provider
- deepseek-flash: DeepSeek V4.1 Flash, good quality, 1M context
- No reasoning: Faster responses (set to "high" or "max" to enable thinking mode)

---

### Example 2: Quality-Focused Setup

**Use Case**: Complex problem-solving, quality priority

```toml
[llm]
provider = "openai"
model = "gpt-6.1-sol"
thinking_level = "medium"

[language]
code = "en"
```

**Rationale**:
- OpenAI: Advanced reasoning capabilities
- gpt-6.1-sol: Default GPT-6 flagship, always reasons
- Temperature: Fixed at 1.0 for all OpenAI models (per expert, not set here)
- Medium thinking: Balanced reasoning

---

### Example 3: Multilingual Setup

**Use Case**: Chinese language optimization

```toml
[llm]
provider = "zai"
model = "glm-5.3"
thinking_level = "high"

[language]
code = "zh-CN"
```

**Rationale**:
- Z.AI: GLM models optimized for Chinese
- Simplified Chinese: Primary language
- High reasoning effort: GLM-5.3 always reasons (low/high/max)

---

### Example 4: Development Setup

**Use Case**: Development and testing

```toml
[llm]
provider = "deepseek"
model = "deepseek-flash"
thinking_level = "none"

[language]
code = "en"
```

**Rationale**:
- DeepSeek: Cost-effective for testing
- No reasoning: Faster iterations
- English: Universal development language

---

## Defaults vs. Expert-Specific Settings

### Understanding Precedence

**Priority Order**:
1. **Expert Config** (per-expert setting; chat toolbox changes are saved here immediately)
2. **App Defaults** (global default, used when creating an expert)
3. **Application Defaults** (hardcoded fallback in `lib/shared/constants.py`)

**Example**: Model setting
```
User picks a model in the chat toolbox → saved to configs/{expert_id}.yaml
    ↓
Expert config metadata.model → used for every request
    ↓
App defaults model → only preselected when creating a new expert
    ↓
Application fallback → deepseek-flash (DEFAULT_LLM_MODEL)
```

**Result**: The expert config wins

### When Defaults Apply

**Defaults apply to**:
- ✅ New experts created after setting defaults
- ✅ Experts without explicit settings
- ✅ Application initialization

**Defaults don't apply to**:
- ❌ Existing experts (they keep their settings)
- ❌ Expert-specific configuration

**Example Workflow**:
```toml
# Initial: App defaults model = "deepseek-flash"

# Create Expert A → Uses deepseek-flash
# Create Expert B → Uses deepseek-flash

# Change app defaults to provider = "openai", model = "gpt-6.1-sol"

# Create Expert C → Uses gpt-6.1-sol (new default)
# Expert A → Still uses deepseek-flash (existing)
# Expert B → Still uses deepseek-flash (existing)

# Switch Expert A to glm-5.3 in the chat toolbox

# Expert A → Uses glm-5.3 (expert-specific)
# App defaults → Still gpt-6.1-sol
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

Temperature is set per expert (dialog or chat toolbox), not in `app_defaults.toml`:
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
model = "gpt-6.1-sol"  # Wrong! gpt-6.1-sol is OpenAI
```

**Solution**: Match provider with correct model:
```toml
# VALID
provider = "openai"
model = "gpt-6.1-sol"  # Correct!
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

**Location**: `.streamlit/app_defaults.toml.example`

```toml
# Application Default Settings
# This file persists your default LLM and other app-wide settings
#
# Copy this file to app_defaults.toml and customize it with your preferences
# The app will automatically create app_defaults.toml when you save settings
# through the UI, but you can also create/edit this file manually
#
# Location: .streamlit/app_defaults.toml
# Permissions: 600 (read/write for owner only)

[llm]
# Default LLM provider
# Options: deepseek, openai, zai, kimi
provider = "deepseek"

# Default model for the selected provider
# DeepSeek: deepseek-flash, deepseek-v4-pro
# OpenAI: gpt-6.1-sol, gpt-6-astra, gpt-6-luna, gpt-5.6-sol, gpt-5.6-terra,
#         gpt-5.6-luna, gpt-5.4-mini, gpt-5.4-nano
# Z.AI: glm-5.3, glm-5.2, glm-5, glm-4.7-flash (free)
# KIMI: kimi-k3, kimi-k2.7-code, kimi-k2.7-code-highspeed, kimi-k2.6
model = "deepseek-flash"

# Default thinking/reasoning level
# OpenAI GPT-6.1 Sol / GPT-6 Astra: low, medium, high, xhigh (always reason)
# OpenAI GPT-6 Luna / GPT-5.x: none, low, medium, high, xhigh
# Z.AI GLM-5.3: low, high, max | GLM-5.2: high, max | older GLM: enabled, disabled
# KIMI K3: low, high, max | K2.7 Code: always thinks | K2.6: enabled, disabled
# DeepSeek: none, high, max
thinking_level = "high"

[language]
# Default interface language
# Options: en, de, es, fr, it, pt, ru, tr, id, ms, zh-CN, zh-TW, wyw, yue
# The app will auto-detect your system language on first run
code = "en"

[display]
# Show Git branch in sidebar footer
# Set to false to hide the Git branch display
git_branch = true
```

## Next Steps

- **[Configuration Overview](overview.md)** - Configuration system overview
- **[User Guide - Customization](../user-guide/customization.md)** - Settings page usage
- **[API Providers Guide](../api/providers.md)** - Provider-specific details

---

**Back to**: [Documentation Home](../README.md) | [Configuration Overview](overview.md)
