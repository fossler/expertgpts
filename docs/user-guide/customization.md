# Customization Guide

This guide explains how to customize ExpertGPTs to match your preferences, including themes, language settings, and default configurations.

## Overview

ExpertGPTs offers extensive customization options:
- **Theme customization** - Preset themes and custom colors
- **Language settings** - UI language and expert response language
- **Provider defaults** - Default LLM provider, model and thinking mode

All settings are managed through the **Settings** page and persisted in configuration files.

## Accessing Settings

Navigate to **Settings** from the sidebar:
- Click on **:material/settings:** in the navigation menu

The Settings page has six tabs:
1. **General** - Theme and language
2. **API Key** - Manage API keys for all providers
3. **Default LLM** - Default provider, model and thinking mode for new experts
4. **Expert Management** - Add, edit and delete experts
5. **Danger Zone** - Download all configurations (ZIP), reset the application
6. **About** - Version information and acknowledgments

## Theme Customization

### Understanding Themes

ExpertGPTs uses Streamlit's theming system, which allows you to customize:
- **Primary Color** - Buttons and interactive elements
- **Background Color** - Main content area background
- **Secondary Background Color** - Sidebar and secondary areas
- **Text Color** - Main text color

### Customizing Colors

1. Go to **Settings** → **General** tab
2. Find the **Theme Customization** section
3. Select **🎨 Custom** (the color pickers are only editable for the Custom theme)
4. Use the color pickers in **Color Preview** to adjust:
   - **Buttons and interactive Elements**
   - **Background Color**
   - **Secondary Background** (sidebar)
   - **Text Color**
5. Click **"💾 Save & Apply Theme"** to save (the page reloads)

**Tips**:
- Use high contrast for text readability
- Test colors with dark/light mode considerations
- Preview changes before applying

### Preset Themes

ExpertGPTs includes preset themes for quick customization:

**Light Themes**:
- 🔴 **Modern Red**
- 🔵 **Ocean Blue**
- 🟢 **Forest Green**
- 🟣 **Royal Purple**

**Dark Themes**:
- 🌑 **Dark Blue**
- 🖤 **Dark Gray**

**Applying a Preset**:
1. Go to **Settings** → **General** tab
2. Select a theme under **Select a theme to preview** (the Color Preview updates)
3. Click **"💾 Save & Apply Theme"**; the page reloads with the new theme

The theme files live in `.streamlit/themes/` (one `.toml` file per theme, `custom.toml` for the Custom theme).

### Default Theme

If no `.streamlit/config.toml` exists, it is created from `.streamlit/config.toml.example`, which uses the **Dark Gray** theme.

### Where Theme Settings Are Stored

The selected theme is saved to `.streamlit/config.toml` as a reference to its theme file:

```toml
[theme]
base = ".streamlit/themes/dark_gray.toml"
```

**File location**: `.streamlit/config.toml`
**Permissions**: Automatically set to 600 (secure)
**Git status**: Ignored (not tracked in version control)

## Language Settings

### Supported Languages

ExpertGPTs supports **14 languages** with full UI translations:

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

### Changing Language

1. Go to **Settings** → **General** tab
2. Find the **Language** section (languages are grouped by script)
3. Click the button of your preferred language
4. The preference is saved and the app reloads in the selected language

### Language Behavior

**UI Elements**:
- All buttons, labels, menus translate immediately
- Navigation items update to selected language
- Settings page updates to selected language
- Expert names (default experts) translate

**Expert Responses**:
- Experts automatically respond in your selected language
- Language prefix injected at runtime: "You must respond in German (Deutsch)."
- Works for all experts, regardless of creation language

**Expert Content**:
- Expert names, descriptions, and system prompts remain in English in YAML configs
- Only UI elements are translated
- This ensures single source of truth for expert definitions

### Language Persistence

Your language preference is saved to `.streamlit/app_defaults.toml`:

```toml
[language]
code = "de"  # German
```

**Auto-Detection**:
- First run: System language detected automatically
- Saved to `app_defaults.toml`
- App starts in detected language

**Manual Change**:
- Override via Settings page
- New preference saved
- Persists across app restarts

### Creating Multilingual Experts

You can create experts in any language:
1. Use a description in your language; the name may only contain ASCII letters, numbers, spaces, `_`, `-` and `.` (e.g., "Datenexperte")
2. Expert responds in user's selected language automatically
3. Expert names are only translated for the default (example) experts

**Example**:
- The default expert "Data Scientist" is shown with its translated name in the navigation when German is selected
- A custom expert "Datenexperte" keeps its name in every UI language
- Both get responses in the user's selected language

**See also**: [Internationalization Guide](../internationalization/I18N_GUIDE.md) for detailed i18n documentation

## Provider and Model Defaults

### Setting Default Provider

Choose your preferred LLM provider:

1. Go to **Settings** → **Default LLM** tab
2. Find **Default Provider** dropdown (only providers with an API key are listed)
3. Select provider (DeepSeek, OpenAI, Z.AI, KIMI)
4. Click **"💾 Save Defaults"**

**Impact**:
- New experts use this provider by default
- Can override per-expert
- Current experts unaffected

### Setting Default Model

Choose the default model for your provider:

1. Go to **Settings** → **Default LLM** tab
2. Find **Default Model** dropdown
3. Select model from available options
4. Click **"💾 Save Defaults"**

**Available Models**:
- **DeepSeek**: `deepseek-flash`, `deepseek-v4-pro`
- **OpenAI**: `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.4-mini`, `gpt-5.4-nano`
- **Z.AI**: `glm-5.3`, `glm-5.2`, `glm-5`, `glm-4.7-flash`
- **KIMI**: `kimi-k3`, `kimi-k2.7-code`, `kimi-k2.7-code-highspeed`, `kimi-k2.6`

**Impact**:
- New experts use this model by default
- Can override per-expert
- Current experts unaffected

### Temperature for New Experts

There is no default temperature setting. The temperature is set per expert in the **Add Chat** form (default 1.0) and can be changed later below the chat input. Z.AI accepts at most 1.0; OpenAI and KIMI models use a fixed temperature.

**Temperature Guide**:
- **0.0 - 0.3**: Focused, deterministic (coding, math)
- **0.4 - 0.7**: Balanced (general advice, explanations)
- **0.8 - 1.2**: Creative (brainstorming, analysis)
- **1.3 - 2.0**: Highly creative (creative writing, ideation)

**See also**: [Temperature Guide](temperature-guide.md) for detailed explanations

### Setting Default Thinking Level

Enable/disable reasoning for new experts by default:

1. Go to **Settings** → **Default LLM** tab
2. Find the **Thinking Mode** selector below the default model
3. Select a level (the options depend on the selected model)
4. Click **"💾 Save Defaults"**

**Availability**:
- **OpenAI**: GPT-6.1 Sol / GPT-6 Astra: low/medium/high/xhigh; other models: none/low/medium/high/xhigh
- **DeepSeek**: none/high/max
- **Z.AI**: GLM-5.3: low/high/max; GLM-5.2: high/max; GLM-5 / GLM-4.7-Flash: enabled/disabled
- **KIMI**: K3: low/high/max; K2.7 Code: always on; K2.6: enabled/disabled

**Impact**:
- New experts use this thinking level by default
- Can override per-expert
- Current experts unaffected

**Note**: Reasoning increases response time and cost. Use for complex tasks.

## API Key Management

### Setting API Keys

ExpertGPTs supports multiple LLM providers, each requiring an API key.

**Via Settings Page** (Recommended):

1. Go to **Settings** → **API Key** tab
2. Select the provider under **Select LLM Provider** (DeepSeek, OpenAI, Z.AI, KIMI)
3. Enter API key in the input field
4. Click **"Save API Key"** (**Clear** removes the saved key)
5. Key automatically saved to `.streamlit/secrets.toml`

**Manual Configuration**:

1. Copy example file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml`:
   ```toml
   DEEPSEEK_API_KEY = "your_actual_api_key_here"
   OPENAI_API_KEY = "your_actual_api_key_here"
   ZAI_API_KEY = "your_actual_api_key_here"
   MOONSHOT_API_KEY = "your_actual_api_key_here"  # KIMI
   ```

### API Key Sources

Get API keys from:
- **DeepSeek**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Z.AI**: [https://z.ai/](https://z.ai/)
- **KIMI**: [https://platform.kimi.ai/console](https://platform.kimi.ai/console)

### API Key Security

**Security Measures**:
- **File location**: `.streamlit/secrets.toml` (gitignored)
- **File permissions**: Automatically set to 600 (owner read/write only)
- **Validation**: Provider-specific key format check (e.g. DeepSeek and KIMI keys start with `sk-`); the error message shows an example of the expected format
- **UI management**: Use Settings page for secure handling

**Verify Permissions**:
```bash
ls -la .streamlit/secrets.toml
# Should show: -rw-------
```

**Multiple Providers**:
You can configure API keys for all providers simultaneously:
- Switch between experts using different providers
- No need to re-enter keys
- Each expert uses its configured provider

## Advanced Customization

### Manual Configuration File Editing

For advanced users, configuration files can be edited directly:

#### Theme Settings

**File**: `.streamlit/config.toml`

```toml
[theme]
base = ".streamlit/themes/ocean_blue.toml"
```

Custom colors are stored in `.streamlit/themes/custom.toml`.

#### App Defaults

**File**: `.streamlit/app_defaults.toml`

```toml
[llm]
provider = "deepseek"
model = "deepseek-flash"
thinking_level = "high"

[language]
code = "en"

[display]
git_branch = true   # show the git branch in the sidebar footer
```

#### API Keys

**File**: `.streamlit/secrets.toml`

```toml
DEEPSEEK_API_KEY = "your_key_here"
OPENAI_API_KEY = "your_key_here"
ZAI_API_KEY = "your_key_here"
MOONSHOT_API_KEY = "your_key_here"
```

**Warning**: Manual editing requires caution. Use UI when possible.

### Resetting to Defaults

**Reset Theme**:
1. Go to **Settings** → **General** tab
2. Select a preset theme (e.g., Dark Gray, the default) and click **"💾 Save & Apply Theme"**
3. Or delete `.streamlit/config.toml` and restart (it is recreated from `config.toml.example`)

**Reset App Defaults**:
1. Delete `.streamlit/app_defaults.toml`
2. Restart app (auto-detects language, sets defaults)

**Reset All Settings**:
```bash
rm .streamlit/config.toml
rm .streamlit/app_defaults.toml
# Note: API keys in secrets.toml must be re-entered
```

## Customization Best Practices

### 1. Use Preset Themes First

Start with preset themes before customizing colors manually:
- Ensures good color combinations
- Maintains accessibility
- Faster than manual customization

### 2. Set Provider Defaults Wisely

Choose defaults based on your typical use:
- **Cost-conscious**: DeepSeek (most cost-effective)
- **Quality-focused**: OpenAI (advanced reasoning)
- **Multilingual**: Z.AI (Chinese language optimization)

### 3. Choose Appropriate Temperatures

Set per expert based on its primary use case:
- **Technical work**: 0.3 - 0.5
- **General advisory**: 0.6 - 0.8
- **Creative work**: 0.9 - 1.2

### 4. Test Theme Changes

Always preview theme changes:
- Check text readability
- Ensure good contrast
- Test with different content types

## Troubleshooting

### Theme Not Applying

**Problem**: Changed colors but theme doesn't update

**Solutions**:
1. Click **"💾 Save & Apply Theme"** button
2. Refresh browser (F5 or Cmd+R)
3. Clear browser cache
4. Check `.streamlit/config.toml` for correct values

### Language Not Changing

**Problem**: Selected different language but UI still in English

**Solutions**:
1. App restarts automatically - wait for reload
2. Check browser cache (clear and reload)
3. Verify language saved to `app_defaults.toml`
4. Try selecting language again

### API Key Not Saving

**Problem**: Entered API key but getting "invalid key" error

**Solutions**:
1. Verify the key matches the provider's format (the error message shows an example)
2. Check for extra spaces (copy-paste carefully)
3. Confirm key is correct from provider dashboard
4. Check `.streamlit/secrets.toml` permissions (should be 600)

### Defaults Not Applying to New Experts

**Problem**: Created expert but it doesn't use default provider/model

**Explanation**: Defaults only apply to **new** experts created after setting defaults.

**Solution**:
- Set defaults first
- Then create new experts
- Or manually edit existing experts

## Next Steps

- **[Temperature Guide](temperature-guide.md)** - Master temperature settings
- **[Configuration Guide](../configuration/overview.md)** - Understand configuration system
- **[API Keys Guide](../configuration/api-keys.md)** - Detailed API key management
- **[Internationalization Guide](../internationalization/I18N_GUIDE.md)** - Comprehensive i18n documentation

---

**Back to**: [Documentation Home](../README.md) | [User Guide - Basics](basics.md)
