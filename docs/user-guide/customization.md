# Customization Guide

This guide explains how to customize ExpertGPTs to match your preferences, including themes, language settings, and default configurations.

## Overview

ExpertGPTs offers extensive customization options:
- **Theme customization** - Colors, fonts, appearance
- **Language settings** - UI language and expert response language
- **Provider defaults** - Default LLM provider and model
- **App preferences** - Various application defaults

All settings are managed through the **Settings** page and persisted in configuration files.

## Accessing Settings

Navigate to **Settings** from the sidebar:
- Click on **:material/settings:** in the navigation menu

The Settings page has three tabs:
1. **General** - Theme, language, and app defaults
2. **API Keys** - Manage API keys for all providers
3. **About** - Version information and acknowledgments

## Theme Customization

### Understanding Themes

ExpertGPTs uses Streamlit's theming system, which allows you to customize:
- **Primary Color** - Buttons and interactive elements
- **Background Color** - Main content area background
- **Secondary Background Color** - Sidebar and secondary areas
- **Text Color** - Main text color
- **Font Family** - Text font (sans-serif, serif, monospace)

### Customizing Colors

1. Go to **Settings** → **General** tab
2. Find the **Theme Customization** section
3. Use the color pickers to adjust:
   - **Buttons and Interactive Elements**
   - **Background Color**
   - **Secondary Background** (sidebar)
   - **Text Color**
4. Click **"Apply Changes"** to save

**Tips**:
- Use high contrast for text readability
- Test colors with dark/light mode considerations
- Preview changes before applying

### Preset Themes

ExpertGPTs includes preset themes for quick customization:

**Light Themes**:
- 🎨 **Red** - Warm red accents
- 🎨 **Blue** - Professional blue
- 🎨 **Green** - Calming green
- 🎨 **Purple** - Creative purple

**Dark Themes**:
- 🌙 **Dark Blue** - Dark blue with bright accents
- 🌙 **Dark Gray** - Minimalist dark theme

**Applying a Preset**:
1. Go to **Settings** → **General** tab
2. Click on any preset theme button
3. Theme applies immediately

### Default Theme

The app comes with a modern **Indigo** theme by default:
- **Buttons**: Indigo (#6366F1)
- **Background**: White (#FFFFFF)
- **Sidebar**: Light Gray (#F3F4F6)
- **Text**: Dark Gray (#1F2937)

### Where Theme Settings Are Stored

Theme settings are saved to `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#6366F1"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"
```

**File location**: `.streamlit/config.toml`
**Permissions**: Automatically set to 600 (secure)
**Git status**: Ignored (not tracked in version control)

## Language Settings

### Supported Languages

ExpertGPTs supports **13 languages** with full UI translations:

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
2. Find the **Language** dropdown
3. Select your preferred language
4. Click outside the dropdown to save
5. App restarts automatically in selected language

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
1. Use name and description in your language (e.g., "Datenexperte")
2. Expert responds in user's selected language automatically
3. Expert name translates if it's a default expert

**Example**:
- Create "Datenexperte" (German name)
- English user sees "Data Expert" (translated)
- German user sees "Datenexperte" (original)
- Both users get responses in their selected language

**See also**: [Internationalization Guide](../internationalization/I18N_GUIDE.md) for detailed i18n documentation

## Provider and Model Defaults

### Setting Default Provider

Choose your preferred LLM provider:

1. Go to **Settings** → **General** tab
2. Find **Default Provider** dropdown
3. Select provider (DeepSeek, OpenAI, Z.AI)
4. Click outside dropdown to save

**Impact**:
- New experts use this provider by default
- Can override per-expert
- Current experts unaffected

### Setting Default Model

Choose the default model for your provider:

1. Go to **Settings** → **General** tab
2. Find **Default Model** dropdown
3. Select model from available options
4. Click outside dropdown to save

**Available Models**:
- **DeepSeek**: `deepseek-chat`, `deepseek-reasoner`
- **OpenAI**: `o3-mini`, `gpt-4o`, `gpt-4o-mini`
- **Z.AI**: `glm-4.7`, `glm-4.7-thinking`

**Impact**:
- New experts use this model by default
- Can override per-expert
- Current experts unaffected

### Setting Default Temperature

Set the default temperature for new experts:

1. Go to **Settings** → **General** tab
2. Find **Default Temperature** slider
3. Adjust to desired value (0.0 - 2.0)
4. Click outside slider to save

**Temperature Guide**:
- **0.0 - 0.3**: Focused, deterministic (coding, math)
- **0.4 - 0.7**: Balanced (general advice, explanations)
- **0.8 - 1.2**: Creative (brainstorming, analysis)
- **1.3 - 2.0**: Highly creative (creative writing, ideation)

**See also**: [Temperature Guide](temperature-guide.md) for detailed explanations

**Impact**:
- New experts use this temperature by default
- Can override per-expert
- Current experts unaffected

### Setting Default Thinking Level

Enable/disable reasoning for new experts by default:

1. Go to **Settings** → **General** tab
2. Find **Default Thinking Level** dropdown
3. Select level (None, Low, Medium, High)
4. Click outside dropdown to save

**Availability**:
- **OpenAI**: All levels supported
- **DeepSeek**: Enabled/disabled based on model
- **Z.AI**: Enabled/disabled via extra_body

**Impact**:
- New experts use this thinking level by default
- Can override per-expert
- Current experts unaffected

**Note**: Reasoning increases response time and cost. Use for complex tasks.

## API Key Management

### Setting API Keys

ExpertGPTs supports multiple LLM providers, each requiring an API key.

**Via Settings Page** (Recommended):

1. Go to **Settings** → **API Keys** tab
2. Select provider from tabs (DeepSeek, OpenAI, Z.AI)
3. Enter API key in the input field
4. Click **"Save API Key"**
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
   ```

### API Key Sources

Get API keys from:
- **DeepSeek**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Z.AI**: [https://z.ai/](https://z.ai/)

### API Key Security

**Security Measures**:
- **File location**: `.streamlit/secrets.toml` (gitignored)
- **File permissions**: Automatically set to 600 (owner read/write only)
- **Validation**: Minimum 20 characters required
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
primaryColor = "#6366F1"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"
```

#### App Defaults

**File**: `.streamlit/app_defaults.toml`

```toml
[llm]
provider = "deepseek"
model = "deepseek-chat"
thinking_level = "none"

[language]
code = "en"
```

#### API Keys

**File**: `.streamlit/secrets.toml`

```toml
DEEPSEEK_API_KEY = "your_key_here"
OPENAI_API_KEY = "your_key_here"
ZAI_API_KEY = "your_key_here"
```

**Warning**: Manual editing requires caution. Use UI when possible.

### Resetting to Defaults

**Reset Theme**:
1. Go to **Settings** → **General** tab
2. Click on a preset theme (e.g., Indigo default)
3. Or delete `.streamlit/config.toml` and restart

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

### 3. Choose Appropriate Temperature Defaults

Set based on your primary use case:
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
1. Click **"Apply Changes"** button
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
1. Verify key is at least 20 characters
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
